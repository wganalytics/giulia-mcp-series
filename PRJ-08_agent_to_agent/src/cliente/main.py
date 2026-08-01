import sys
from post_crew import PostCrew

if __name__ == "__main__":
    tema = " ".join(sys.argv[1:]).strip() or input("Tema do post: ").strip()
    if not tema:
        print("Informe um tema. Ex.: uv run python src/cliente/main.py \"IA na educação\"")
        sys.exit(1)
    crew = PostCrew()
    print(f"Executando post_crew com o tema: {tema}")
    result = crew.kickoff(inputs={"tema": tema})
    print("\n--- RESULTADO FINAL ---")
    print(result)
