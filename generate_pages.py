import os

# Configuration
plots_dir = "plots"
output_dir = "."
image_exts = [".png", ".jpg", ".jpeg", ".pdf"]

# Utilities
def format_md_link(name):
    return name.replace(" ", "_").replace("/", "_").lower()

def make_markdown_header(title, back_link=True):
    header = f"# {title} Network Simulation Plots\n"
    if back_link:
        header += "\n[⬅️ Back to Home](index.md)\n"
    header += "\n---\n"
    return header

def make_collapsible_section(title, content, level=0):
    margin = "margin-left: 10px;" if level > 0 else ""
    return (
        f"<details style='{margin}'>\n"
        f"<summary><strong>{title}</strong></summary>\n\n"
        f"{content}\n"
        f"</details>\n"
    )

def embed_image(path):
    ext = os.path.splitext(path)[1].lower()
    path = path.replace(" ", "%20")  # URL-safe
    if ext == ".pdf":
        return f'<embed src="{path}" width="100%" height="600px" type="application/pdf" style="margin-bottom: 20px; border: 1px solid #ccc;" />\n'
    else:
        return f'<img src="{path}" alt="{os.path.basename(path)}" width="700px" style="margin-bottom: 20px; border: 1px solid #ccc; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" />\n'

def generate_network_md(network):
    network_dir = os.path.join(plots_dir, network)
    markdown_lines = [make_markdown_header(network)]

    for dist in sorted(os.listdir(network_dir)):
        dist_path = os.path.join(network_dir, dist)
        if not os.path.isdir(dist_path):
            continue

        dist_sections = []
        for mass in sorted(os.listdir(dist_path)):
            mass_path = os.path.join(dist_path, mass)
            if not os.path.isdir(mass_path):
                continue

            images = [
                f for f in sorted(os.listdir(mass_path))
                if os.path.splitext(f)[1].lower() in image_exts
            ]
            if not images:
                continue

            content = "".join([
                embed_image(os.path.join("plots", network, dist, mass, img).replace("\\", "/"))
                for img in images
            ])
            dist_sections.append(make_collapsible_section(mass, content, level=1))

        if dist_sections:
            markdown_lines.append(make_collapsible_section(dist, "\n".join(dist_sections)))

    return "\n\n".join(markdown_lines)

# Generate homepage
networks = [d for d in sorted(os.listdir(plots_dir)) if os.path.isdir(os.path.join(plots_dir, d))]
with open(os.path.join(output_dir, "index.md"), "w") as f:
    f.write("# BBH Simulation Results\n\n")
    f.write("Explore detector network simulations below:\n\n")
    for net in networks:
        link = format_md_link(net) + ".md"
        f.write(f"- [{net}]({link})\n")

# Generate network-specific pages
for net in networks:
    md_content = generate_network_md(net)
    out_path = os.path.join(output_dir, format_md_link(net) + ".md")
    with open(out_path, "w") as f:
        f.write(md_content)

