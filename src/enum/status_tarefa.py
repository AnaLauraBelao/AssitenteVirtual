from enum import Enum

class StatusAtividade(Enum):
    CONCLUIDA = "concluida"
    EM_ANDAMENTO = "em_andamento"
    IMPEDIDA = "impedida"
    NAO_INICIADA = "nao_iniciada"

    @classmethod
    def legivel(cls, valor):
        mapeamento = {
            cls.CONCLUIDA.value: "Concluída",
            cls.EM_ANDAMENTO.value: "Em andamento",
            cls.IMPEDIDA.value: "Impedida",
            cls.NAO_INICIADA.value: "Não Iniciada",
        }
        return mapeamento.get(valor, valor)