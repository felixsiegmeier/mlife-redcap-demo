from services.headers import headers

def split_blocks(file: str, DELIMITER: str) -> dict:
    lines = file.splitlines()
    result = {category: {} for category in headers}
    
    current_category = None
    current_block = None
    buffer = []

    def flush_buffer():
        nonlocal buffer, current_category, current_block
        if current_category and current_block:
            result[current_category][current_block] = "\n".join(buffer).strip()
        buffer = []

    for line in lines:
        key = line.split(DELIMITER, 1)[0].strip()

        found = False
        for category, blocks in headers.items():
            if key in blocks:
                flush_buffer()
                current_category = category
                current_block = key
                found = True
                break

        if not found:
            buffer.append(line)

    flush_buffer()

    return result