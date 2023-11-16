import fitz
import os
import pandas as pd

def check_underline(underline, bbox):
    items = underline.get("items", [])

    left, top, right, bottom = items[0][1]

    # checks if there is sufficient overlap between the underline and the box
    if left - 0.1 <= bbox[0] <= left + 0.1 and bbox[3]-1.75<= bottom <= bbox[3]+1.75 and right <=bbox[2]+0.1:
        return True
    return False

def extract_text_with_styles(paths,page):
    blocks = page.get_text("dict")["blocks"]
    text_with_styles = []

    # Extract text with styles
    words = page.get_text("words")
    arects = [fitz.Rect(w[:4]) for w in words]
    count=0
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"]
                    color = span["color"]
                    size = span["size"]
                    bbox = fitz.Rect(span["bbox"])

                    # Convert the color to hex format
                    if isinstance(color, int):
                        color_hex = "#{:06x}".format(color)
                    else:
                        color_hex = "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))

                    is_underlined=False

                    if(text and count<len(paths)):
                        is_underlined=check_underline(paths[count],span["bbox"])
                        if(is_underlined):
                            count= count+1


                    text_with_styles.append({
                        "text": text.strip(),
                        "color": color_hex,
                        "size": size,
                        "bbox": bbox,
                        "underlined": is_underlined
                    })

    return text_with_styles

def draw_rectangles(page, text_with_styles):
    for style_info in text_with_styles:
        bbox = style_info["bbox"]
        page.draw_rect(bbox, color=(1, 0, 0), width=2)


def create_csv_pdf(file_path):

  doc = fitz.open(file_path)

  # Extract text and styles again with the corrected code
  text_with_styles_per_page = {}
  # Iterate through each page

  for page_num in range(len(doc)):
        page = doc[page_num]
        output_path = f"underlined_pages/underline_page_{page_num}.pdf"

        #find all the underlines in a page
        paths = page.get_drawings()
        path_rects = [fitz.Rect(path["rect"]) for path in paths]

        for path_rect in path_rects:
            page.draw_rect(path_rect, color=(1, 0, 0), width=2)
        
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        new_doc.save(output_path)
        new_doc.close()
        
        text_with_styles = extract_text_with_styles(paths,page)
        
        # Save the page with the rectangles and the underlines both
        # draw_rectangles(page, text_with_styles)

        # new_doc = fitz.open()
        # new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
        # new_doc.save(f"full_page_{page_num}.pdf")
        # new_doc.close()
        
        print(text_with_styles)

        text_with_styles_per_page[page_num] = text_with_styles




def process_pdfs_in_directory():
    directory_path='./test_files'

    files_and_directories = os.listdir(directory_path)
    # Filter out directories, keep only files
    files = [os.path.join(directory_path, f) for f in files_and_directories if os.path.isfile(os.path.join(directory_path, f))]

    pdf_core = pd.DataFrame()

    for pdf_name in files:
        create_csv_pdf(pdf_name)


def main():
    process_pdfs_in_directory()
    
if __name__ == "__main__":
    main()