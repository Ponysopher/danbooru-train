import sys


def format_size(size_bytes):
    if size_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f}{size_name[i]}"


def print_memory_size(obj, obj_name="Object"):
    size_bytes = sys.getsizeof(obj)
    formatted_size = format_size(size_bytes)
    print(f"{obj_name} memory size: {formatted_size}")
