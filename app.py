# GUI skeleton 
import tkinter as tk

def main():
    root = tk.Tk()
    root.title("Custom TTS App")
    root.geometry("600x400")

    # Input box
    input_label = tk.Label(root, text="Enter Text:")
    input_label.pack(pady=5)
    input_box = tk.Text(root, height=5, width=50)
    input_box.pack(pady=5)

    # Buttons
    preprocess_btn = tk.Button(root, text="Preprocess")
    preprocess_btn.pack(pady=5)

    tts_btn = tk.Button(root, text="Generate Speech")
    tts_btn.pack(pady=5)

    # Output / log area
    output_label = tk.Label(root, text="Output / Logs will appear here")
    output_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
