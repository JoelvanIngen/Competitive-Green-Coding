LANG_TAGS = ["C", "Python", "Java", "Rust", "JavaScript", "Golang", "C++"]
DIFF_TAGS = ["easy", "medium", "hard"]
PROBLEM_TAGS = ["type #1", "type #2", "type #3", "type #4", "type #5"]

TAGS = LANG_TAGS + DIFF_TAGS + PROBLEM_TAGS


def translate_tags_to_bitmap(tags: list[str]) -> int:
    bitmap = 0
    for tag in tags:
        try:
            index = TAGS.index(tag)
            bitmap |= 1 << index
        except ValueError:
            continue
    return bitmap


def translate_bitmap_to_tags(bitmap: int) -> list[str]:
    tags = []
    for i in range(len(TAGS)):
        if bitmap & (1 << i):
            tags.append(TAGS[i])
    extra_bits = bitmap >> len(TAGS)
    index = len(TAGS)
    while extra_bits:
        if extra_bits & 1:
            tags.append(f"unknown_tag_{index}")
        extra_bits >>= 1
        index += 1
    return tags
