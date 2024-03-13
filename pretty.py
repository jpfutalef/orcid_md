import markdown


def df_to_markdown(df, save_to="./publication_record.md"):
    md = []
    for year, items in df.groupby("year", sort=True):
        for _, item in items.iterrows():
            md.append(item["reference"])
            md.append("")
        md.append(f"## {year}")
        md.append("")
    mds = "\n".join(md[::-1][1:])

    # Write to a markdown file
    with open(save_to, "w", encoding='utf-8') as f:
        f.write(mds)

    return mds


def markdown_to_html(mds, save_to="./publication_record.html"):
    html = markdown.markdown(mds)
    with open(save_to, "w", encoding='utf-8') as f:
        f.write(html)

    return html
