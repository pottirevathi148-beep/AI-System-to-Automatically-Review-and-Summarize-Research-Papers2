import gradio as gr
import fitz  # PyMuPDF
import matplotlib.pyplot as plt

# -------- Extract RAW text --------
def extract_text(file):
    text = ""
    pdf = fitz.open(file.name)

    for page in pdf:
        text += page.get_text()

    return text  # keep raw (with \n)


# -------- Clean text --------
def clean_text(text):
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


# -------- Summary --------
def summarize(text):
    if not text.strip():
        return "⚠️ No content found"
    return text[:500] + "..."


# -------- Section Detection (FINAL FIX) --------
def detect_sections(text):
    abstract = ""
    methods = ""
    results = ""

    lines = text.split("\n")
    current = None

    for line in lines:
        l = line.lower()

        if "abstract" in l:
            current = "abstract"

        elif ("method" in l or "methodology" in l 
              or "experimental" in l or "approach" in l):
            current = "methods"

        elif ("result" in l or "evaluation" in l 
              or "performance" in l or "experiment" in l):
            current = "results"

        if current == "abstract":
            abstract += line + " "

        elif current == "methods":
            methods += line + " "

        elif current == "results":
            results += line + " "

    # -------- CLEAN FORMAT --------
    abstract = " ".join(abstract.split())
    methods = " ".join(methods.split())
    results = " ".join(results.split())

    # fallback
    if not methods:
        methods = "⚠️ Methods section not detected"

    if not results:
        results = "⚠️ Results section not detected"

    return abstract[:600], methods[:600], results[:600]


# -------- Keywords --------
def extract_keywords(text):
    words = text.split()
    freq = {}

    for word in words:
        word = word.lower().strip(".,()")
        if len(word) > 4:
            freq[word] = freq.get(word, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    top_words = sorted_words[:8]

    keywords = [w[0] for w in top_words]

    return keywords, dict(top_words)


# -------- Graph --------
def plot_graph(freq_dict):
    if not freq_dict:
        return None

    words = list(freq_dict.keys())
    counts = list(freq_dict.values())

    plt.figure(figsize=(10, 5))
    plt.bar(words, counts)

    plt.title("Top Keywords Frequency")
    plt.xlabel("Keywords")
    plt.ylabel("Count")

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return plt


# -------- Main --------
def process_pdf(file):
    raw_text = extract_text(file)

    clean = clean_text(raw_text)

    summary = summarize(clean)

    # use RAW text for section detection
    abstract, methods, results = detect_sections(raw_text)

    keywords, freq_dict = extract_keywords(clean)

    graph = plot_graph(freq_dict)

    return (
        clean[:800],
        summary,
        abstract,
        methods,
        results,
        ", ".join(keywords),
        graph
    )


# -------- UI --------
with gr.Blocks() as app:
    gr.Markdown("## 📄 PDF Analyzer (Sections + Graph 📊)")

    file_input = gr.File(label="Upload PDF")

    extracted = gr.Textbox(label="📜 Extracted Text", lines=6)
    summary = gr.Textbox(label="🧠 Summary", lines=4)

    abstract = gr.Textbox(label="📑 Abstract", lines=3)
    methods = gr.Textbox(label="⚙️ Methods", lines=3)
    results = gr.Textbox(label="📊 Results", lines=3)

    keywords = gr.Textbox(label="🔑 Keywords")
    graph = gr.Plot(label="📊 Keyword Graph")

    btn = gr.Button("Analyze")

    btn.click(
        process_pdf,
        inputs=file_input,
        outputs=[extracted, summary, abstract, methods, results, keywords, graph]
    )

app.launch()