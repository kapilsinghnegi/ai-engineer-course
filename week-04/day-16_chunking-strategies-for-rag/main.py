from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)

text = """
The detective entered the abandoned house just before midnight. The rooms were silent, and the windows were covered with dust. On the table, he found a bloodstained letter that mentioned a secret meeting.

The man who did the crime was John. Nobody in the village trusted him, but he had disappeared three days before the murder. The detective immediately realized that John had left behind one important clue.

The next morning, the detective returned to the house. Behind a loose brick, he discovered a photograph of John standing beside the victim. This finally connected John to the crime.    
"""

# 1. Fixed-size chunking
fixed = CharacterTextSplitter(separator="", chunk_size=100, chunk_overlap=0)

print("\n============== FIXED SIZE ==============")

for i, chunk in enumerate(fixed.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print(
        "==================================================================================================="
    )

# 2. Paragraph Chunking
paragraph = CharacterTextSplitter(separator="\n\n", chunk_size=100, chunk_overlap=0)

print("\n============== PARAGRAPH ==============")

for i, chunk in enumerate(paragraph.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print(
        "==================================================================================================="
    )

# 3. Recursive Chunking
recursive = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

print("\n============== RECURSIVE ==============")

for i, chunk in enumerate(recursive.split_text(text), 1):
    print(f"\nChunk {i}:")
    print(chunk)
    print(
        "==================================================================================================="
    )
