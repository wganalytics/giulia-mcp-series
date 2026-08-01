"""Testes das tools do servidor de ping.

`check_host` abre uma conexão TCP de verdade — os testes sobem um socket local em
porta efêmera, então nada sai da máquina.
"""
import socket
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from ping_server import check_host, echo, ping  # noqa: E402


@pytest.fixture
def porta_aberta():
    """Sobe um listener TCP em porta efêmera e devolve o número."""
    servidor = socket.socket()
    servidor.bind(("127.0.0.1", 0))
    servidor.listen(1)
    yield servidor.getsockname()[1]
    servidor.close()


@pytest.fixture
def porta_fechada():
    """Reserva uma porta e a libera — quase certamente ninguém escuta nela."""
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    porta = s.getsockname()[1]
    s.close()
    return porta


# --------------------------------------------------------------------------
# ping / echo
# --------------------------------------------------------------------------

def test_ping_responde_pong():
    assert ping() == "pong"


@pytest.mark.parametrize("mensagem", ["oi", "", "acentuação é ok", "com\nquebra", "🎯"])
def test_echo_devolve_exatamente_a_mensagem(mensagem):
    assert echo(mensagem) == mensagem


# --------------------------------------------------------------------------
# check_host — health-check TCP real
# --------------------------------------------------------------------------

def test_host_acessivel_reporta_up(porta_aberta):
    resultado = check_host("127.0.0.1", porta_aberta, timeout=2.0)
    assert resultado.startswith(f"UP 127.0.0.1:{porta_aberta}")


def test_host_acessivel_reporta_latencia_em_ms(porta_aberta):
    resultado = check_host("127.0.0.1", porta_aberta, timeout=2.0)
    latencia = resultado.split("—")[1].strip()
    assert latencia.endswith(" ms")
    assert float(latencia.removesuffix(" ms")) >= 0


def test_porta_fechada_reporta_down(porta_fechada):
    assert check_host("127.0.0.1", porta_fechada, timeout=1.0).startswith("DOWN")


def test_host_inexistente_reporta_down_sem_levantar():
    """Falha de DNS/rede vira mensagem, não exceção — a tool não pode derrubar o server."""
    assert check_host("host.invalido.teste", 443, timeout=1.0).startswith("DOWN")


def test_timeout_e_respeitado():
    """10.255.255.1 é um endereço não roteável: a conexão pendura até o timeout."""
    import time
    inicio = time.perf_counter()
    resultado = check_host("10.255.255.1", 65000, timeout=0.5)
    decorrido = time.perf_counter() - inicio
    assert resultado.startswith("DOWN")
    assert decorrido < 3.0, "o timeout precisa limitar a espera"


def test_porta_padrao_e_443():
    import inspect
    assinatura = inspect.signature(check_host)
    assert assinatura.parameters["port"].default == 443
    assert assinatura.parameters["timeout"].default == 3.0
