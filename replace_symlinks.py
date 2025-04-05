import os
import shutil

def replace_symlinks(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for name in dirnames + filenames:
            full_path = os.path.join(dirpath, name)
            if os.path.islink(full_path):
                real_path = os.readlink(full_path)

                # Absolute symlinks (e.g., /home/liampond/...) — we resolve them as-is
                if not os.path.isabs(real_path):
                    real_path = os.path.join(os.path.dirname(full_path), real_path)

                print(f"Replacing symlink: {full_path} -> {real_path}")

                # Remove the symlink
                os.unlink(full_path)

                # Copy the real file/folder in its place
                if os.path.isdir(real_path):
                    shutil.copytree(real_path, full_path)
                else:
                    shutil.copy2(real_path, full_path)

if __name__ == "__main__":
    replace_symlinks(".")  # Run in current directory
