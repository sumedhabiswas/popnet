import os

plots_dir = "plots"
output_file = "index.md"
image_exts = [".png", ".jpg", ".jpeg", ".pdf"]
plot_map = {}

for root, dirs, files in os.walk(plots_dir):
    rel_dir = os.path.relpath(root, plots_dir)
    rel_dir = "." if rel_dir == "." else rel_dir.replace("\\", "/")
    
    image_files = [f for f in sorted(files) if os.path.splitext(f)[1].lower() in image_exts]
    if image_files:
        plot_map[rel_dir] = image_files

lines = ["# BBH Simulation Plots", "\n"]
lines.append("## Navigation")
for folder in sorted(plot_map.keys()):
    if folder == ".":
        continue
    anchor = folder.replace(" ", "-").replace("/", "-")
    lines.append(f"- [{folder}](#{anchor.lower()})")
lines.append("")

for folder, images in sorted(plot_map.items()):
    title = "Main Plots" if folder == "." else folder
    anchor = folder.replace(" ", "-").replace("/", "-").lower()

    lines.append(f"\n<a name=\"{anchor}\"></a>")
    lines.append(f"<details>\n<summary><strong>{title}</strong></summary>\n")

    for img in images:
        path = os.path.join(plots_dir, folder, img).replace("\\", "/")
        lines.append(f"<img src=\"{path}\" alt=\"{img}\" width=\"600px\" style=\"margin-bottom: 10px;\" />")

    lines.append("</details>\n")

with open(output_file, "w") as f:
    f.writelines(line + "\n" for line in lines)

