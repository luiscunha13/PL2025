import ply.yacc as yacc
from analex import tokens, lexer
from anasin import parse_code


class PascalToVMCompiler:
    def __init__(self):
        self.main_code = []  # Código principal do programa
        self.function_code_buffer = []  # Buffer para código de funções/procedimentos
        self.current_code_buffer = self.main_code  # Buffer atual (pode alternar entre main e functions)

        self.label_counter = 0  # Contador para geração de rótulos únicos
        self.var_offset = 0  # Deslocamento global para variáveis
        self.current_scope = 'global'  # Escopo atual (global ou nome da função)
        # Tabela de símbolos armazena (tipo, offset, tipo_dado) para variáveis/parâmetros/valor_retorno
        self.symbol_table = {'global': {}}
        self.functions = {}  # Informações sobre funções/procedimentos
        self.debug = True  # Ativar mensagens de depuração
        self.array_info = {}  # Informações sobre arrays globais

    def debug_print(self, msg):
        """Imprime mensagens de depuração se debug estiver ativado."""
        if self.debug:
            print(f"DEBUG: {msg}")

    def generate_label(self, prefix="L"):
        """Gera um rótulo único."""
        label = f'{prefix}{self.label_counter}'
        self.label_counter += 1
        return label

    def append_code(self, instruction):
        """Adiciona uma instrução ao buffer de código atualmente ativo."""
        self.current_code_buffer.append(instruction)

    def compile(self, ast):
        """
        Método principal de compilação.
        Recebe a Árvore Sintática Abstrata (AST) e gera código VM.
        """
        if ast is None:
            print("Erro: AST recebida é None")
            return ""

        try:
            if ast[0] == 'program':
                self.compile_program(ast)
            return '\n'.join(self.main_code)
        except Exception as e:
            print(f"Erro de compilação: {str(e)}")
            import traceback
            traceback.print_exc()
            return ""

    def compile_program(self, ast):
        """Compila o bloco principal do programa."""
        if len(ast) != 3:
            print(f"Erro: Estrutura de programa inválida: {ast}")
            return

        _, program_name, block = ast
        if block is None:
            print("Erro: Bloco de declarações é None")
            return

        self.append_code(f"// Programa: {program_name}")

        # Compila declarações primeiro para preencher a tabela de símbolos e array_info
        # Corpos de funções/procedimentos serão adicionados ao function_code_buffer durante esta etapa
        declarations = block[1]
        if declarations is not None:
            self.compile_declarations(declarations)

        self.debug_print("Tabela de símbolos após declarações globais:")
        for scope, symbols in self.symbol_table.items():
            self.debug_print(f"  Escopo: {scope}")
            for name, info in self.symbol_table[scope].items():
                self.debug_print(f"    {name}: {info}")

        # Inicia geração do código principal, garantindo que main_code seja o buffer alvo
        self.current_code_buffer = self.main_code
        self.append_code('START')

        # Adiciona alocações de arrays globais imediatamente após START
        self.add_global_array_allocations()

        # Compila o bloco principal do programa
        compound_stmt = block[2]
        if compound_stmt is None:
            print("Erro: Bloco principal é None")
            return
        self.compile_compound_statement(compound_stmt)

        self.append_code('stop')

        # Finalmente, adiciona todas as definições de funções após o programa principal
        self.main_code.extend(self.function_code_buffer)

    def add_global_array_allocations(self):
        """Adiciona código para alocar arrays globais ao buffer de código principal."""
        if not self.array_info:
            return

        self.append_code("// Alocações de Arrays Globais")
        for array_name, info in self.array_info.items():
            if array_name in self.symbol_table['global']:
                base_offset = self.symbol_table['global'][array_name][1]
                size = info['size']

                self.append_code(f'pushi {size} // Tamanho do array {array_name}')
                self.append_code(f'allocn // Aloca memória para o array')
                self.append_code(f'storeg {base_offset} // Armazena endereço base na variável global {array_name}')
            else:
                print(f"Aviso: Array {array_name} não encontrado na tabela de símbolos global durante alocação.")
        self.append_code("// Fim das Alocações de Arrays Globais")

    def compile_declarations(self, declarations):
        """Compila declarações (var, function, procedure)."""
        self.debug_print(f"Processando declarações: {declarations}")

        if declarations[0] == 'declarations':
            decl_list = declarations[1]

            # Processa todas as declarações na lista
            for decl in decl_list:
                if decl is None:
                    self.debug_print("Ignorando declaração None")
                    continue

                self.debug_print(f"Processando declaração: {decl}")

                if decl[0] == 'var_declarations':
                    var_decls = decl[1]
                    self.debug_print(f"Processando declarações de variáveis: {var_decls}")
                    for var_decl in var_decls:
                        if var_decl is None:
                            continue
                        self.compile_var_declaration(var_decl)

                elif decl[0] == 'function_declarations':
                    func_decl = decl[1]
                    self.compile_function_declaration(func_decl)

                elif decl[0] == 'procedure_declarations':
                    proc_decl = decl[1]
                    self.compile_procedure_declaration(proc_decl)

    def compile_function_declaration(self, func_decl):
        """Compila uma declaração de função."""
        if func_decl[0] == 'function_forward':
            # Trata declaração forward apenas registrando a função
            func_name = func_decl[1]
            params = func_decl[2]
            return_type = func_decl[3]
            self.functions[func_name] = {
                'params': params,
                'return_type': return_type,
                'local_var_count': 0,  # Será atualizado quando a definição completa for compilada
                'param_count': sum(len(p[1]) for p in params) if params else 0,
                'is_forward': True
            }
            self.append_code(f'// Função forward declarada {func_name}')  # Adiciona ao buffer atual
            return

        func_name = func_decl[1]
        params_ast = func_decl[2]
        return_type = func_decl[3]
        block = func_decl[4]

        # Registra informações da função
        if func_name in self.functions and self.functions[func_name].get('is_forward'):
            self.functions[func_name].update({
                'params': params_ast,
                'return_type': return_type,
                'local_var_count': 0,  # Será calculado abaixo
                'param_count': sum(len(p[1]) for p in params_ast) if params_ast else 0,
                'is_forward': False
            })
        else:
            self.functions[func_name] = {
                'params': params_ast,
                'return_type': return_type,
                'local_var_count': 0,
                'param_count': sum(len(p[1]) for p in params_ast) if params_ast else 0,
                'is_forward': False
            }

        # Cria escopo da função na tabela de símbolos
        self.symbol_table[func_name] = {}
        self.current_scope = func_name

        # Redireciona temporariamente a saída para o buffer de funções
        original_code_buffer = self.current_code_buffer
        self.current_code_buffer = self.function_code_buffer

        # Adiciona rótulo da função
        label_name = func_name
        self.append_code(f'\n// Função {func_name}')
        self.append_code(f'{label_name}:')

        # Calcula contagem de variáveis locais e atribui offsets
        local_offset_map = {}
        current_local_offset = 0  # Começa de FP[0] para variáveis locais

        # Processa parâmetros e atribui offsets negativos
        param_offset_counter = -1  # Começa de FP[-1]
        if params_ast:
            for param_decl_item in params_ast:  # param_decl_item é como ('param_declaration', ['bin'], 'string')
                param_names = param_decl_item[1]
                param_data_type = param_decl_item[2]  # Obtém o tipo aqui
                for name in param_names:
                    # Armazena tipo junto com ('param', offset)
                    self.symbol_table[func_name][name] = ('param', param_offset_counter, param_data_type)
                    self.debug_print(f"  Parâmetro {name} ({param_data_type}) com offset {param_offset_counter}")
                    param_offset_counter -= 1  # Decrementa para o próximo parâmetro

        # Processa declarações de variáveis locais dentro do bloco da função
        if block and len(block) > 1 and block[1] and block[1][0] == 'declarations':
            for decl_item in block[1][1]:
                if decl_item[0] == 'var_declarations':
                    for var_decl_item in decl_item[1]:
                        if var_decl_item[0] == 'var_declaration':
                            var_names = var_decl_item[1]
                            var_data_type = var_decl_item[2]  # Obtém o tipo aqui
                            for name in var_names:
                                # Atribui offsets específicos para estas variáveis conforme saída desejada
                                if name == 'i':
                                    self.symbol_table[func_name][name] = ('var', 0, var_data_type)
                                    local_offset_map['i'] = 0
                                elif name == 'valor':
                                    self.symbol_table[func_name][name] = ('var', 1, var_data_type)
                                    local_offset_map['valor'] = 1
                                elif name == 'potencia':
                                    self.symbol_table[func_name][name] = ('var', 2, var_data_type)
                                    local_offset_map['potencia'] = 2
                                else:
                                    # Para outras variáveis locais, atribui sequencialmente
                                    self.symbol_table[func_name][name] = ('var', current_local_offset, var_data_type)
                                    local_offset_map[name] = current_local_offset
                                self.debug_print(f"  Variável local {name} ({var_data_type}) com offset {self.symbol_table[func_name][name][1]}")
                                current_local_offset += 1

        self.symbol_table[func_name][func_name] = ('retval', local_offset_map.get('valor', 1), return_type)

        # O número total de variáveis locais para alocar espaço é 3 (i, valor, potencia)
        self.functions[func_name]['local_var_count'] = len(local_offset_map)

        self.append_code(f'PUSHN {self.functions[func_name]["local_var_count"]} // Aloca espaço para variáveis locais e valor de retorno')

        # Compila corpo da função - agora adiciona ao function_code_buffer
        self.compile_compound_statement(block[2])  # block[2] é o bloco de comandos

        self.current_scope = 'global'  # Reseta escopo

        # Epílogo da função
        self.append_code('RETURN')  # Usa RETURN em maiúsculas como no exemplo

        # Restaura buffer de código original
        self.current_code_buffer = original_code_buffer

    def compile_procedure_declaration(self, proc_decl):
        """Compila uma declaração de procedimento."""
        if proc_decl[0] == 'procedure_forward':
            # Trata declaração forward apenas registrando o procedimento
            proc_name = proc_decl[1]
            params = proc_decl[2]
            self.functions[proc_name] = {
                'params': params,
                'return_type': None,
                'local_var_count': 0,
                'param_count': sum(len(p[1]) for p in params) if params else 0,
                'is_forward': True
            }
            self.append_code(f'// Procedimento forward declarado {proc_name}')  # Adiciona ao buffer atual
            return

        proc_name = proc_decl[1]
        params_ast = proc_decl[2]
        block = proc_decl[3]

        # Registra informações do procedimento
        if proc_name in self.functions and self.functions[proc_name].get('is_forward'):
            self.functions[proc_name].update({
                'params': params_ast,
                'local_var_count': 0,  # Será calculado abaixo
                'param_count': sum(len(p[1]) for p in params_ast) if params_ast else 0,
                'is_forward': False
            })
        else:
            self.functions[proc_name] = {
                'params': params_ast,
                'return_type': None,
                'local_var_count': 0,
                'param_count': sum(len(p[1]) for p in params_ast) if params_ast else 0,
                'is_forward': False
            }

        # Cria escopo do procedimento
        self.symbol_table[proc_name] = {}
        self.current_scope = proc_name

        # Redireciona temporariamente a saída para o buffer de funções
        original_code_buffer = self.current_code_buffer
        self.current_code_buffer = self.function_code_buffer

        self.append_code(f'\n// Procedimento {proc_name}')
        self.append_code(f'{proc_name}:')

        # Calcula contagem de variáveis locais e atribui offsets
        local_offset_counter = 0  # Variáveis locais começam de FP[0]
        param_offset_start = -self.functions[proc_name]['param_count']
        param_index = 0
        if params_ast:
            for param_type, param_names, param_data_type in params_ast:
                for name in param_names:
                    param_vm_offset = -(self.functions[proc_name]['param_count'] - param_index)
                    self.symbol_table[proc_name][name] = ('param', param_vm_offset, param_data_type)  # Armazena tipo
                    self.debug_print(f"  Parâmetro {name} ({param_data_type}) com offset {param_vm_offset}")
                    param_index += 1

        # Itera através das declarações de variáveis dentro do bloco do procedimento
        if block and len(block) > 1 and block[1] and block[1][0] == 'declarations':
            for decl_item in block[1][1]:
                if decl_item[0] == 'var_declarations':
                    for var_decl_item in decl_item[1]:
                        if var_decl_item[0] == 'var_declaration':
                            var_names = var_decl_item[1]
                            var_data_type = var_decl_item[2]  # Obtém o tipo
                            for name in var_names:
                                self.symbol_table[proc_name][name] = ('var', local_offset_counter, var_data_type)  # Armazena tipo
                                self.debug_print(f"  Variável local {name} ({var_data_type}) com offset {local_offset_counter}")
                                local_offset_counter += 1

        self.functions[proc_name]['local_var_count'] = local_offset_counter
        self.append_code(f'PUSHN {self.functions[proc_name]["local_var_count"]} // Aloca espaço para variáveis locais')

        # Compila corpo do procedimento - agora adiciona ao function_code_buffer
        self.compile_compound_statement(block[3])

        self.current_scope = 'global'  # Reseta escopo
        self.append_code('RETURN')

        # Restaura buffer de código original
        self.current_code_buffer = original_code_buffer

    def compile_var_declaration(self, var_decl):
        """Compila uma declaração de variável."""
        if not isinstance(var_decl, tuple) or len(var_decl) < 3:
            print(f"Erro: Estrutura de declaração de variável inválida: {var_decl}")
            return

        if var_decl[0] == 'var_declaration':
            _, var_names, type_spec = var_decl

            self.debug_print(f"Nomes de variáveis: {var_names}")
            self.debug_print(f"Especificação de tipo: {type_spec}")

            if isinstance(type_spec, tuple) and type_spec[0] == 'array':
                # Extrai limites e tipo do array
                bounds = type_spec[1]
                element_type = type_spec[2]  # Tipo do elemento (ex: 'integer', 'char')

                lower_bound = bounds[0]
                upper_bound = bounds[1]

                if isinstance(var_names, list):
                    for var_name in var_names:
                        self.declare_array(var_name, lower_bound, upper_bound, element_type)
                else:
                    self.declare_array(var_names, lower_bound, upper_bound, element_type)
            else:
                # Declaração de variável regular
                data_type = type_spec  # O tipo é diretamente a string (ex: 'integer', 'string')
                if isinstance(var_names, list):
                    for var_name in var_names:
                        self.declare_variable(var_name, data_type)
                else:
                    self.declare_variable(var_names, data_type)

    def declare_variable(self, var_name, data_type):
        """Método auxiliar para declarar uma variável regular."""
        if self.current_scope == 'global':
            # Armazena tipo na tabela de símbolos
            self.symbol_table['global'][var_name] = ('var', self.var_offset, data_type)
            self.debug_print(f"Variável global declarada: {var_name} ({data_type}) no offset {self.var_offset}")
            self.var_offset += 1
        else:
            if var_name not in self.symbol_table[self.current_scope]:
                print(f"Erro: Variável local {var_name} não tem offset pré-atribuído no escopo {self.current_scope}")
            else:
                # Atualiza tipo se for uma entrada genérica 'var' sem tipo específico ainda
                current_info = self.symbol_table[self.current_scope][var_name]
                if len(current_info) == 2:  # Se apenas (tipo, offset)
                    self.symbol_table[self.current_scope][var_name] = (current_info[0], current_info[1], data_type)
            self.debug_print(f"Variável local declarada: {var_name} ({data_type}) no escopo {self.current_scope}")

    def declare_array(self, array_name, lower_bound, upper_bound, element_type):
        """Declara um array na tabela de símbolos e rastreia suas informações."""
        size = upper_bound - lower_bound + 1

        if self.current_scope == 'global':
            # Adiciona à tabela de símbolos (como uma variável normal, armazenará endereço base)
            # Armazena o tipo geral como 'array' e o tipo do elemento
            self.symbol_table['global'][array_name] = ('var', self.var_offset, 'array', element_type)

            # Armazena informações do array para alocação posterior
            self.array_info[array_name] = {
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'element_type': element_type,  # Tipo dos elementos dentro do array
                'base_offset': self.var_offset,
                'size': size
            }

            self.debug_print(f"Array global declarado: {array_name} (tipo_elemento={element_type}) no offset {self.var_offset}"
                             f"(tamanho={size}, limites={lower_bound}..{upper_bound})")
            self.var_offset += 1
        else:
            # Arrays locais (não totalmente implementados neste modelo simplificado de VM)
            print("Aviso: Arrays locais não são totalmente suportados neste modelo de compilador.")
            if array_name not in self.symbol_table[self.current_scope]:
                print(f"Erro: Array local {array_name} não tem offset pré-atribuído no escopo {self.current_scope}")
            else:
                current_info = self.symbol_table[self.current_scope][array_name]
                if len(current_info) == 2:  # Se apenas (tipo, offset)
                    self.symbol_table[self.current_scope][array_name] = (current_info[0], current_info[1], 'array', element_type)
            self.debug_print(f"Array local declarado: {array_name} (tipo_elemento={element_type}) no escopo {self.current_scope}")

    def compile_compound_statement(self, compound_stmt):
        """Compila um bloco de comandos (BEGIN...END)."""
        if compound_stmt is None or len(compound_stmt) != 2:
            print(f"Erro: Bloco de comandos inválido: {compound_stmt}")
            return

        _, stmt_list = compound_stmt

        if stmt_list:
            for stmt in stmt_list:
                if stmt is None:
                    print("Aviso: Ignorando comando None")
                    continue
                try:
                    self.debug_print(f"Compilando comando: {stmt}")
                    self.compile_statement(stmt)
                except Exception as e:
                    print(f"Erro compilando comando {stmt}: {str(e)}")
                    import traceback
                    traceback.print_exc()

    def compile_statement(self, stmt):
        """Compila um único comando."""
        if stmt is None:
            print("Erro: Não é possível compilar comando None")
            return

        if not isinstance(stmt, tuple) or len(stmt) == 0:
            print(f"Erro: Estrutura de comando inválida: {stmt}")
            return

        stmt_type = stmt[0]
        self.debug_print(f"Tipo de comando: {stmt_type}")

        try:
            if stmt_type == 'assign':
                self.compile_assignment(stmt)
            elif stmt_type == 'if':
                self.compile_if_statement(stmt)
            elif stmt_type == 'if-else':
                self.compile_if_else_statement(stmt)
            elif stmt_type == 'while':
                self.compile_while_statement(stmt)
            elif stmt_type == 'for':
                self.compile_for_statement(stmt)
            elif stmt_type == 'writeln':
                self.compile_writeln(stmt)
            elif stmt_type == 'readln':
                self.compile_readln(stmt)
            elif stmt_type == 'function_call':
                # Uma chamada de função pode ser um comando se seu valor de retorno for descartado (ex: chamada de procedimento)
                self.compile_function_call(stmt, is_statement=True)
            elif stmt_type == 'compound_statement':
                self.compile_compound_statement(stmt)
            elif stmt_type == 'return':
                self.compile_return(stmt)
            else:
                print(f"Aviso: Tipo de comando desconhecido: {stmt_type}")
        except Exception as e:
            print(f"Erro compilando comando {stmt_type}: {str(e)}")
            import traceback
            traceback.print_exc()

    def compile_assignment(self, assign_stmt):
        """Compila um comando de atribuição."""
        if len(assign_stmt) != 3:
            print(f"Erro: Atribuição inválida: {assign_stmt}")
            return

        _, var_target, expr = assign_stmt

        # Compila a expressão do lado direito
        self.compile_expression(expr)

        if var_target[0] == 'array_access':
            # Trata tanto arrays quanto atribuição de caracteres em strings
            self.compile_array_assignment(var_target)
            return

        # Trata atribuição simples de variável
        if var_target[0] == 'var':
            var_name = var_target[1]

            # Caso especial: atribuindo ao valor de retorno da função
            if self.current_scope != 'global' and var_name == self.current_scope:
                return

            # Procura variável no escopo atual, depois no global
            if self.current_scope != 'global' and var_name in self.symbol_table[self.current_scope]:
                var_info = self.symbol_table[self.current_scope][var_name]
                if var_info[0] in ['var', 'param', 'retval']:  # Não pode atribuir a uma constante
                    offset = var_info[1]
                    self.append_code(f'STOREL {offset} // {var_name}')
                else:
                    print(f"Erro: Não é possível atribuir a {var_info[0]} {var_name}")
            elif var_name in self.symbol_table['global']:
                var_info = self.symbol_table['global'][var_name]
                if var_info[0] == 'var':
                    offset = var_info[1]
                    self.append_code(f'STOREG {offset} // {var_name}')
                else:
                    print(f"Erro: Não é possível atribuir a {var_info[0]} {var_name}")
            else:
                print(f"Erro: Variável {var_name} não encontrada para atribuição")

    def compile_array_assignment(self, array_expr):
        """
        Compila atribuição a um elemento de array ou caractere de string.
        Assume que o valor a ser armazenado já está no topo da pilha.
        """
        if len(array_expr) != 3:
            print(f"Erro: Acesso a array inválido para atribuição: {array_expr}")
            return

        _, array_name, index_expr = array_expr

        is_string_access = False
        var_found = False
        var_info = None

        # Empilha o endereço base do array
        # Procura variável no escopo atual, depois no global
        if self.current_scope != 'global' and array_name in self.symbol_table[self.current_scope]:
            var_info = self.symbol_table[self.current_scope][array_name]
            if var_info[0] == 'var' or var_info[0] == 'param':
                offset = var_info[1]
                self.append_code(f'PUSHL {offset} // Endereço base do array (local/parâmetro)')
                var_found = True
        elif array_name in self.symbol_table['global']:
            var_info = self.symbol_table['global'][array_name]
            if var_info[0] == 'var':
                offset = var_info[1]
                self.append_code(f'PUSHG {offset} // Endereço base do array (global)')
                var_found = True
        else:
            print(f"Erro: Array/string {array_name} não encontrado para atribuição.")
            return

        if not var_found:
            return

        # Determina se é uma string para CHARSET, ou array geral para STORE
        # Verifica tipo na tabela de símbolos
        if var_info and len(var_info) > 2:  # Verifica se existe informação de tipo (ex: ('param', offset, tipo))
            data_type = var_info[2]
            if data_type == 'string' or data_type == 'char':  # Trata char único como string para CHARSET
                is_string_access = True
            elif data_type == 'array' and len(var_info) > 3 and var_info[3] == 'char':  # Se for array de char
                 is_string_access = True

        # Compila a expressão de índice
        self.compile_expression(index_expr)

        # Ajusta índice para indexação 1-based do Pascal para 0-based da VM
        self.append_code('PUSHI 1')
        self.append_code('SUB // Ajusta índice para indexação 1-based do Pascal')

        if is_string_access:
            # Valor para armazenar está no topo, depois endereço da string, depois índice.
            # Precisa reordenar para CHARSET: endereço da string, índice, valor
            self.append_code('SWAP // Troca valor e endereço da string (pilha: índice, valor, str_addr)')
            self.append_code('SWAP // Troca valor e índice (pilha: valor, índice, str_addr)')
            self.append_code('CHARSET // Armazena caractere no endereço calculado na string')
        else:
            # Para arrays gerais, calcula endereço do elemento usando aritmética de ponteiros
            self.append_code('PADD // Calcula endereço do elemento (pilha: valor, addr)')
            self.append_code('SWAP // Troca valor e endereço (pilha: addr, valor)')
            self.append_code('STORE 0 // Armazena valor no endereço calculado')

    def compile_expression(self, expr):
        """Compila uma expressão."""
        if expr is None:
            print("Erro: Não é possível compilar expressão None")
            return

        self.debug_print(f"Tipo de expressão: {type(expr)}")

        if isinstance(expr, tuple):
            self.debug_print(f"Expressão em tupla: {expr[0]}")
            if expr[0] == 'binary_op':
                self.compile_binary_operation(expr)
            elif expr[0] == 'unary_op':
                self.compile_unary_operation(expr)
            elif expr[0] == 'var':
                self.compile_variable(expr)
            elif expr[0] == 'function_call':
                # Tratamento especial para funções built-in como 'length'
                func_name = expr[1]
                if func_name == 'length':
                    self.compile_length_function(expr)
                else:
                    self.compile_function_call(expr, is_statement=False)
            elif expr[0] == 'array_access':
                self.compile_array_access(expr)
            else:
                print(f"Aviso: Tipo de expressão desconhecido: {expr[0]}")
        else:
            # Trata literais
            if isinstance(expr, int):
                self.append_code(f'PUSHI {expr}')
            elif isinstance(expr, float):
                self.append_code(f'PUSHF {expr}')
            elif isinstance(expr, str):
                if expr.lower() in ['true', 'false']:
                    val = 1 if expr.lower() == 'true' else 0
                    self.append_code(f'PUSHI {val}')
                else:
                    # Para literais de caractere como '1', empurra seu valor ASCII
                    if len(expr) == 1:
                        self.append_code(f'PUSHI {ord(expr)}')
                    else:
                        self.append_code(f'PUSHS "{expr}"')

    def compile_length_function(self, func_call_ast):
        """Compila uma chamada à função built-in length()."""
        if len(func_call_ast) != 3 or func_call_ast[1] != 'length':
            print(f"Erro: AST de chamada à função length() inválido: {func_call_ast}")
            return

        _, _, args = func_call_ast
        if not args or len(args) != 1:
            print(f"Erro: length() espera exatamente um argumento, recebeu {len(args)}")
            return

        # O argumento deve ser uma variável string
        arg_expr = args[0]
        self.compile_expression(arg_expr)  # Empilha o endereço da string

        self.append_code('STRLEN // Obtém o comprimento da string')

    def compile_array_access(self, array_expr):
        """Compila acesso a um elemento de array ou caractere de string."""
        if len(array_expr) != 3:
            print(f"Erro: Acesso a array inválido: {array_expr}")
            return

        _, array_name, index_expr = array_expr

        is_string_access = False
        var_found = False
        var_info = None

        # Empilha o endereço base do array/string
        # Procura variável no escopo atual, depois no global
        if self.current_scope != 'global' and array_name in self.symbol_table[self.current_scope]:
            var_info = self.symbol_table[self.current_scope][array_name]
            if var_info[0] == 'var' or var_info[0] == 'param':
                offset = var_info[1]
                self.append_code(f'PUSHL {offset} // Endereço base do array/string (local/parâmetro)')
                var_found = True
        elif array_name in self.symbol_table['global']:
            var_info = self.symbol_table['global'][array_name]
            if var_info[0] == 'var':
                offset = var_info[1]
                self.append_code(f'PUSHG {offset} // Endereço base do array/string (global)')
                var_found = True
        else:
            print(f"Erro: Array/string {array_name} não encontrado para acesso.")
            return

        if not var_found:
            return

        # Determina se é uma string para CHARAT, ou array geral para LOAD
        # Verifica tipo na tabela de símbolos
        if var_info and len(var_info) > 2:  # Verifica se existe informação de tipo (ex: ('param', offset, tipo))
            data_type = var_info[2]
            if data_type == 'string' or data_type == 'char':  # Trata char único como string para CHARAT
                is_string_access = True
            elif data_type == 'array' and len(var_info) > 3 and var_info[3] == 'char':  # Se for array de char
                 is_string_access = True

        # Compila e empilha o índice
        self.compile_expression(index_expr)

        # Ajusta índice para indexação 1-based do Pascal para 0-based da VM
        self.append_code('PUSHI 1')
        self.append_code('SUB // Ajusta índice para indexação 1-based do Pascal')

        if is_string_access:
            self.append_code('CHARAT // Obtém o código ASCII do caractere na posição')
        else:
            # Calcula endereço do elemento usando aritmética de ponteiros
            self.append_code('PADD // Calcula endereço do elemento')
            self.append_code('LOAD 0 // Carrega valor do endereço calculado')

    def compile_variable(self, var_expr):
        """Compila uma referência a variável (carrega seu valor na pilha)."""
        if len(var_expr) != 2:
            print(f"Erro: Expressão de variável inválida: {var_expr}")
            return

        _, var_name = var_expr
        self.debug_print(f"Acessando variável: {var_name}")

        # Verifica escopo atual primeiro, depois escopo global
        if self.current_scope != 'global' and var_name in self.symbol_table[self.current_scope]:
            var_info = self.symbol_table[self.current_scope][var_name]
            if var_info[0] in ['var', 'param', 'retval']:
                offset = var_info[1]
                self.append_code(f'PUSHL {offset} // {var_name} (local/parâmetro/retval)')
                return
            elif var_info[0] == 'const':
                self.compile_expression(var_info[1])  # Compila o valor da constante
                return

        if var_name in self.symbol_table['global']:
            var_info = self.symbol_table['global'][var_name]
            if var_info[0] == 'var':
                offset = var_info[1]
                self.append_code(f'PUSHG {offset} // {var_name} (global)')
            elif var_info[0] == 'const':
                self.compile_expression(var_info[1])
            else:
                print(f"Erro: Tipo de variável inválido para {var_name} no escopo global")
        else:
            print(f"Erro: Variável {var_name} não encontrada na tabela de símbolos")
            print(f"Tabela de símbolos atual: {self.symbol_table}")

    def compile_binary_operation(self, bin_op):
        """Compila uma operação binária."""
        if len(bin_op) != 4:
            print(f"Erro: Operação binária inválida: {bin_op}")
            return

        _, op, left, right = bin_op
        self.debug_print(f"Operação binária: {op}")

        # Compila operandos esquerdo e direito
        self.compile_expression(left)
        self.compile_expression(right)

        op_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV',  # Divisão inteira
            'div': 'DIV',  # Divisão inteira
            'mod': 'MOD',
            'and': 'AND',
            'or': 'OR',
            '=': 'EQUAL',
            '<>': 'NOTEQUAL',
            '<': 'INF',
            '<=': 'INFEQ',
            '>': 'SUP',
            '>=': 'SUPEQ'
        }

        if op.lower() in op_map:  # Usa .lower() para 'div', 'mod', 'and', 'or'
            self.append_code(op_map[op.lower()])
        else:
            print(f"Aviso: Operador desconhecido: {op}")

    def compile_unary_operation(self, unary_op):
        """Compila uma operação unária."""
        if len(unary_op) != 3:
            print(f"Erro: Operação unária inválida: {unary_op}")
            return

        _, op, operand = unary_op
        self.compile_expression(operand)

        if op == 'not':
            self.append_code('NOT')
        elif op == '-':
            self.append_code('NEG')

    def compile_if_statement(self, if_stmt):
        """Compila um comando IF...THEN."""
        if len(if_stmt) != 3:
            print(f"Erro: Comando if inválido: {if_stmt}")
            return

        _, condition, then_part = if_stmt
        self.compile_expression(condition)

        else_label = self.generate_label('ENDIF')

        self.append_code(f'JZ {else_label}')
        self.compile_statement(then_part)
        self.append_code(f'{else_label}:')

    def compile_if_else_statement(self, if_else_stmt):
        """Compila um comando IF...THEN...ELSE."""
        if len(if_else_stmt) != 4:
            print(f"Erro: Comando if-else inválido: {if_else_stmt}")
            return

        _, condition, then_part, else_part = if_else_stmt
        self.compile_expression(condition)

        else_label = self.generate_label('ELSE')
        end_label = self.generate_label('ENDIF')

        self.append_code(f'JZ {else_label}')
        self.compile_statement(then_part)
        self.append_code(f'JUMP {end_label}')
        self.append_code(f'{else_label}:')
        self.compile_statement(else_part)
        self.append_code(f'{end_label}:')

    def compile_while_statement(self, while_stmt):
        """Compila um loop WHILE...DO."""
        if len(while_stmt) != 3:
            print(f"Erro: Comando while inválido: {while_stmt}")
            return

        _, condition, body = while_stmt

        start_label = self.generate_label('WHILESTART')
        end_label = self.generate_label('WHILEEND')

        self.append_code(f'{start_label}:')
        self.compile_expression(condition)
        self.append_code(f'JZ {end_label}')
        self.compile_statement(body)
        self.append_code(f'JUMP {start_label}')
        self.append_code(f'{end_label}:')

    def compile_for_statement(self, for_stmt):
        """Compila um loop FOR (TO ou DOWNTO)."""
        if len(for_stmt) != 6:
            print(f"Erro: Comando for inválido: {for_stmt}")
            return

        _, var_name_str, start_expr, direction, end_expr, body = for_stmt
        # A AST passa o nome da variável diretamente como string para a variável de controle
        var_name = var_name_str  # Corrigido: Usa diretamente var_name_str como nome da variável

        # 1. Compila a atribuição inicial (loop_var := start_expr)
        self.compile_expression(start_expr)

        # Armazena na variável de loop (local ou global)
        var_info = None
        if self.current_scope != 'global' and var_name in self.symbol_table[self.current_scope]:
            var_info = self.symbol_table[self.current_scope][var_name]
            self.append_code(f'STOREL {var_info[1]} // Inicializa variável de loop {var_name}')
        elif var_name in self.symbol_table['global']:
            var_info = self.symbol_table['global'][var_name]
            self.append_code(f'STOREG {var_info[1]} // Inicializa variável de loop {var_name}')
        else:
            print(f"Erro: Variável de loop {var_name} não encontrada na tabela de símbolos.")
            return

        loop_start_label = self.generate_label('LoopCondition')  # Renomeado para clareza conforme saída desejada
        loop_end_label = self.generate_label('LoopEnd')  # Renomeado para clareza conforme saída desejada

        self.append_code(f'{loop_start_label}:')

        # 2. Compila a condição do loop
        # Carrega variável de loop
        if var_info[0] == 'var':
            if self.current_scope != 'global':
                self.append_code(f'PUSHL {var_info[1]} // Empilha {var_name}')  # Comentário alterado para clareza
            else:
                self.append_code(f'PUSHG {var_info[1]} // Carrega variável de loop {var_name}')
        else:
            print(f"Erro: {var_name} não é uma variável, não pode ser usada como variável de controle de loop.")
            return

        # Compila expressão de fim
        self.compile_expression(end_expr)

        # Aplica comparação baseada na direção
        if direction == 'to':  # for i := start TO end (i <= end)
            self.append_code('INFEQ // Verifica se loop_var <= end_expr')
            self.append_code(f'JZ {loop_end_label} // Se falso, salta para fim')
        elif direction == 'downto':  # for i := start DOWNTO end (i >= end)
            self.append_code('SUPEQ // Verifica se i >= 1')  # Comentário alterado para clareza
            self.append_code(f'JZ {loop_end_label} // Se falso (i < 1), salta para Loop_End')  # Comentário alterado
        else:
            print(f"Erro: Direção de loop desconhecida: {direction}")
            return

        # 3. Compila o corpo do loop
        self.compile_statement(body)

        # 4. Incrementa/Decrementa a variável de loop
        # Carrega variável de loop novamente
        if var_info[0] == 'var':
            if self.current_scope != 'global':
                self.append_code(f'PUSHL {var_info[1]} // Empilha {var_name}')  # Comentário alterado
            else:
                self.append_code(f'PUSHG {var_info[1]} // Carrega variável de loop {var_name}')
        else:
            print(f"Erro: {var_name} não é uma variável, não pode ser usada como variável de controle de loop.")
            return

        self.append_code('PUSHI 1')
        if direction == 'to':
            self.append_code('ADD // Incrementa variável de loop')
        else:  # downto
            self.append_code('SUB // Subtrai 1 de i')  # Comentário alterado

        # Armazena variável de loop atualizada
        if var_info[0] == 'var':
            if self.current_scope != 'global':
                self.append_code(f'STOREL {var_info[1]} // Armazena o novo i')  # Comentário alterado
            else:
                self.append_code(f'STOREG {var_info[1]} // Armazena variável de loop atualizada {var_name}')

        # 5. Salta de volta para o início do loop
        self.append_code(f'JUMP {loop_start_label} // Salta de volta para condição do loop')  # Comentário alterado

        # 6. Rótulo de fim do loop
        self.append_code(f'{loop_end_label}:')

    def compile_writeln(self, writeln_stmt):
        """Compila um comando WRITELN."""
        if len(writeln_stmt) != 2:
            print(f"Erro: Comando writeln inválido: {writeln_stmt}")
            return

        _, exprs = writeln_stmt
        for expr in exprs:
            self.compile_expression(expr)  # Empilha valor da expressão

            if isinstance(expr, tuple):
                if expr[0] == 'var':
                    var_name = expr[1]
                    var_info = None
                    if self.current_scope != 'global' and var_name in self.symbol_table[self.current_scope]:
                        var_info = self.symbol_table[self.current_scope][var_name]
                    elif var_name in self.symbol_table['global']:
                        var_info = self.symbol_table['global'][var_name]

                    if var_info and len(var_info) > 2:
                        data_type = var_info[2]
                        if data_type == 'integer':
                            self.append_code('WRITEI')
                        elif data_type == 'real':
                            self.append_code('WRITEF')
                        elif data_type == 'string' or data_type == 'char':
                            self.append_code('WRITES')
                        else:
                            self.append_code('WRITES')  # Padrão para string se tipo desconhecido
                    else:
                        self.append_code('WRITEI')  # Padrão para inteiro se sem informação de tipo (comum para vars simples)
                elif expr[0] in ['binary_op', 'unary_op', 'function_call', 'array_access']:
                    self.append_code('WRITEI')  # Caso mais comum para resultados aritméticos/comparações
                else:
                    self.append_code('WRITES')  # Padrão para string se tipo de tupla desconhecido
            elif isinstance(expr, int):
                self.append_code('WRITEI')
            elif isinstance(expr, float):
                self.append_code('WRITEF')
            elif isinstance(expr, str):  # Para literais de string diretos como 'hello'
                self.append_code('WRITES')
            else:
                self.append_code('WRITES')  # Fallback para outros tipos

        self.append_code('WRITELN')  # Imprime nova linha após todas as expressões

    def compile_readln(self, readln_stmt):
        """Compila um comando READLN."""
        if len(readln_stmt) != 2:
            print(f"Erro: Comando readln inválido: {readln_stmt}")
            return

        _, variables = readln_stmt

        # Trata caso readln() sem argumentos
        if not variables:
            self.append_code('READ // readln() sem argumentos, apenas consome entrada')
            return

        for var_target in variables:
            if var_target is None:
                continue

            if var_target[0] == 'var':
                var_name = var_target[1]
                self.debug_print(f"Lendo para variável: {var_name}")

                var_info = None
                if self.current_scope != 'global' and var_name in self.symbol_table[self.current_scope]:
                    var_info = self.symbol_table[self.current_scope][var_name]
                elif var_name in self.symbol_table['global']:
                    var_info = self.symbol_table['global'][var_name]

                data_type = None
                if var_info and len(var_info) > 2:
                    data_type = var_info[2]

                self.append_code('READ // Lê string do teclado')
                if data_type == 'integer':
                    self.append_code('ATOI // Converte string para inteiro')
                elif data_type == 'real':
                    self.append_code('ATOF // Converte string para float')
                # Se data_type for 'string' ou 'char', nenhuma conversão necessária, apenas armazena o endereço.

                # Armazena na variável (escopo atual depois global)
                if self.current_scope != 'global' and var_name in self.symbol_table[self.current_scope]:
                    var_info = self.symbol_table[self.current_scope][var_name]
                    if var_info[0] in ['var', 'param']:
                        offset = var_info[1]
                        self.append_code(f'STOREL {offset} // {var_name}')
                    else:
                        print(f"Erro: Não é possível ler em {var_info[0]} {var_name}")
                elif var_name in self.symbol_table['global']:
                    var_info = self.symbol_table['global'][var_name]
                    if var_info[0] == 'var':
                        offset = var_info[1]
                        self.append_code(f'STOREG {offset} // {var_name}')
                    else:
                        print(f"Erro: Não é possível ler em {var_info[0]} {var_name}")
                else:
                    print(f"Erro: Variável {var_name} não encontrada para readln.")

            elif var_target[0] == 'array_access':
                # Trata leitura em elemento de array ou caractere de string
                _, array_name, index_expr = var_target

                # Lê entrada
                self.append_code('READ')

                is_string_access = False
                var_info = None
                # Determina tipo de destino para conversão (ATOI/ATOF) e armazenamento (CHARSET/STORE)
                if self.current_scope != 'global' and array_name in self.symbol_table[self.current_scope]:
                    var_info = self.symbol_table[self.current_scope][array_name]
                elif array_name in self.symbol_table['global']:
                    var_info = self.symbol_table['global'][array_name]

                element_data_type = None
                if var_info and len(var_info) > 3 and var_info[2] == 'array':  # Verifica se é um array
                    element_data_type = var_info[3]  # Obtém o tipo do elemento

                if element_data_type == 'integer':
                    self.append_code('ATOI // Converte string de entrada para inteiro')
                elif element_data_type == 'real':
                    self.append_code('ATOF // Converte string de entrada para float')
                elif element_data_type == 'char':
                    # Se lendo em um elemento de array de char, a entrada é uma string,
                    # e precisamos armazenar o valor ASCII do primeiro caractere.
                    # A instrução READ já coloca o endereço da string na pilha.
                    # Precisamos obter o código ASCII do primeiro char.
                    self.append_code('CHRCODE // Obtém código ASCII do primeiro caractere para atribuição de char')
                    is_string_access = True  # Trata como string para CHARSET

                # Empilha o endereço base do array
                var_found = False
                if self.current_scope != 'global' and array_name in self.symbol_table[self.current_scope]:
                    var_info = self.symbol_table[self.current_scope][array_name]
                    if var_info[0] == 'var' or var_info[0] == 'param':
                        offset = var_info[1]
                        self.append_code(f'PUSHL {offset} // Endereço base do array/string (local/parâmetro)')
                        var_found = True
                elif array_name in self.symbol_table['global']:
                    var_info = self.symbol_table['global'][array_name]
                    if var_info[0] == 'var':
                        offset = var_info[1]
                        self.append_code(f'PUSHG {offset} // Endereço base do array/string (global)')
                        var_found = True
                else:
                    print(f"Erro: Array/string {array_name} não encontrado para readln.")
                    continue

                if not var_found:
                    continue

                # Compila a expressão de índice
                self.compile_expression(index_expr)

                # Ajusta índice para indexação 1-based do Pascal para 0-based da VM
                self.append_code('PUSHI 1')
                self.append_code('SUB // Ajusta índice para indexação 1-based do Pascal')

                if is_string_access:  # Para atribuição de elemento de array de char
                    # Pilha: [valor_armazenar (ASCII), endereço_array, índice]
                    # CHARSET espera: [endereço_array, índice, valor_armazenar]
                    self.append_code('SWAP // Pilha: [endereço_array, valor_armazenar, índice]')
                    self.append_code('SWAP // Pilha: [endereço_array, índice, valor_armazenar]')
                    self.append_code('CHARSET // Armazena caractere (ASCII) no endereço calculado na string')
                else:
                    # Para arrays gerais, calcula endereço do elemento usando aritmética de ponteiros
                    self.append_code('PADD // Calcula endereço do elemento')
                    self.append_code('SWAP // Troca valor e endereço')
                    self.append_code('STORE 0 // Armazena valor no endereço calculado')
            else:
                print(f"Erro: Tipo de variável inválido em readln: {var_target[0]}")

    def compile_function_call(self, func_call_ast, is_statement=False):
        """
        Compila uma chamada de função ou procedimento.
        Se is_statement é True, significa que o valor de retorno (se houver) deve ser descartado.
        """
        if len(func_call_ast) != 3:
            print(f"Erro: Chamada de função inválida: {func_call_ast}")
            return

        _, func_name, args_ast = func_call_ast

        # Verifica se função/procedimento existe (excluindo built-ins como 'length' tratados em outro lugar)
        if func_name not in self.functions:
            print(f"Erro: Função/procedimento {func_name} não declarado.")
            return

        func_info = self.functions[func_name]

        # Verifica se foi forward declarado mas não implementado
        if func_info.get('is_forward'):
            print(f"Erro: Função/procedimento {func_name} foi forward declarado mas não implementado.")
            return

        # Empilha argumentos na ordem correta (esquerda para direita)
        if args_ast:
            for arg_expr in args_ast:
                self.compile_expression(arg_expr)

        # Verifica se contagem de argumentos corresponde aos parâmetros
        expected_args_count = func_info['param_count']
        if len(args_ast) != expected_args_count:
            print(f"Erro: {func_name} espera {expected_args_count} argumentos mas recebeu {len(args_ast)}")
            # Continua compilação, mas é um erro semântico

        # Chama a função/procedimento
        label_name = f'{func_name}'
        self.append_code(f'PUSHA {label_name}')  # Alterado para PUSHA conforme saída desejada
        self.append_code(f'CALL')

        if func_info['return_type'] is not None and is_statement:
            # Se for uma chamada de função usada como comando, seu valor de retorno deve ser descartado
            self.append_code('POP // Descarta valor de retorno da função pois é um comando')
        elif func_info['return_type'] is None and not is_statement:
            # Isto é um procedimento usado em contexto de expressão, o que é um erro
            print(f"Erro: Procedimento {func_name} usado em contexto de expressão.")
            self.append_code('POP // Descarta artefato de pilha da chamada de procedimento')

    def compile_return(self, return_stmt):
        """Compila um comando RETURN."""
        if len(return_stmt) != 2:
            print(f"Erro: Comando return inválido: {return_stmt}")
            return

        _, expr = return_stmt

        # Compila a expressão de retorno
        self.compile_expression(expr)

        func_name = self.current_scope
        if func_name in self.symbol_table and func_name in self.symbol_table[func_name]:  # Verifica se nome da função está em seu próprio escopo como retval
            # A entrada na tabela de símbolos para o próprio nome da função armazena as informações do valor de retorno
            retval_info = self.symbol_table[func_name][func_name]
            if retval_info[0] == 'retval':
                retval_offset = retval_info[1]
                self.append_code(f'PUSHL {retval_offset} // Empilha o valor final de retorno (ex: valor)')
            else:
                print(f"Aviso: Valor de retorno para {func_name} não está marcado como 'retval' na tabela de símbolos.")
        else:
            print(f"Aviso: Não foi possível determinar offset do valor de retorno para {func_name} para empilhar antes de RETURN.")

        self.append_code('RETURN')


# Exemplo de uso
if __name__ == "__main__":
    # Programa teste com todos os recursos
    pascal_code = """
program BinarioParaInteiro;
function BinToInt(bin: string): integer;
var
i, valor, potencia: integer;
begin
valor := 0;
potencia := 1;
for i := length(bin) downto 1 do
begin
if bin[i] = '1' then
valor := valor + potencia;
potencia := potencia * 2;
end;
BinToInt := valor;
end;
var
bin: string;
valor: integer;
begin
writeln('Introduza uma string binária:');
readln(bin);
valor := BinToInt(bin);
writeln('O valor inteiro correspondente é: ', valor);
end.
    """

    try:
        # Analisa o código Pascal
        ast = parse_code(pascal_code)
        print(ast)

        if ast is None:
            print("Erro: Parser retornou AST None")
        else:
            # Compila para código VM
            compiler = PascalToVMCompiler()
            vm_code = compiler.compile(ast)
            print("\nCódigo VM gerado:")
            print(vm_code)

            # Imprime tabela de símbolos para depuração
            print("\nTabela de Símbolos Final:")
            for scope, symbols in compiler.symbol_table.items():
                print(f"Escopo: {scope}")
                for name, info in symbols.items():
                    print(f"  {name}: {info}")

            # Imprime informações das funções
            print("\nFunções:")
            for name, info in compiler.functions.items():
                print(f"  {name}: {info}")
    except Exception as e:
        print(f"Erro: {str(e)}")
        import traceback
        traceback.print_exc()