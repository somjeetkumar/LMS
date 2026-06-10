import random
import os
import uuid
import json
from django.conf import settings
from moviepy import VideoFileClip, concatenate_videoclips
from pypdf import PdfReader, PdfWriter
import requests
from PyPDF2 import PdfReader, PdfWriter
from groq import Groq
from dotenv import load_dotenv



import os


load_dotenv()




def generate_mcqs_from_text(text):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
            return {
                "status": False,
                "answer": "GROQ_API_KEY not configured."
            }
    client = Groq(api_key=api_key)

    


    style = random.choice([
        "definition based",
        "scenario based",
        "application based",
        "comparison based",
        "troubleshooting based",
        "best practices based",
        "real world example based",
        "advanced concept based"
    ])

    prompt = f"""
    You are a JSON generator.

    Generate exactly 10 MCQs from the provided text.

    Question style:
    {style}

    STRICT REQUIREMENTS:

    Return ONLY valid JSON.

    Do not write:
    - markdown
    - explanation
    - comments
    - notes
    - headings
    - code blocks

    The response MUST start with '{{' and end with '}}'.

    Use EXACTLY this structure:

    {{
      "questions": [
        {{
          "id": 1,
          "question": "Question text",
          "options": [
            "Option A",
            "Option B",
            "Option C",
            "Option D"
          ],
          "correct_answer": 0
        }}
      ]
    }}

    Rules:

    1. Generate exactly 10 questions.
    2. Use only these keys:
       - questions
       - id
       - question
       - options
       - correct_answer
    3. Never use:
       - index
       - number
       - answer
       - correct
       - solution
    4. options must contain exactly 4 items.
    5. correct_answer must be:
       - 0
       - 1
       - 2
       - 3
    6. IDs must be:
       - 1 to 10
       - unique
    7. Questions must be based only on the provided text.
    8. Return JSON only.

    TEXT:
    {text}
    """

    response = client.chat.completions.create(
        # model="llama3-8b-8192",
        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )
    
    response_text = response.choices[0].message.content
    

    
    response_text = (
    response_text
    .replace("```json", "")
    .replace("```", "")
    .strip()
    )
    

    # questions = json.loads(response_text)
    try:
        questions = json.loads(response_text)
    except json.JSONDecodeError:
        print("Invalid JSON:")
        print(response_text)

    return questions







def doubt_solve(doubt_text):

    try:

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            return {
                "status": False,
                "answer": "GROQ_API_KEY not configured."
            }

        client = Groq(api_key=api_key)

        prompt = f"""
        You are an expert AI Tutor working inside a Learning Management System (LMS).

        STUDENT QUESTION:
        {doubt_text}

        Answer the student's question clearly and simply.
        """

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()

        return {
            "status": True,
            "answer": answer
        }

    except Exception as e:

        print("GROQ ERROR:", str(e))

        return {
            "status": False,
            "answer": str(e)
        }


def attach_demo_pages(sub, demo_pdf_path, full_pdf_path=None):

    demo_reader = PdfReader(demo_pdf_path)
    writer = PdfWriter()

    if full_pdf_path and os.path.exists(full_pdf_path):
        full_reader = PdfReader(full_pdf_path)
        for page in full_reader.pages:
            writer.add_page(page)


    total_pages = len(demo_reader.pages)

    if total_pages < 3:
        for page in demo_reader.pages:
            writer.add_page(page)
    else:
        quarter = total_pages // 4
        writer.add_page(demo_reader.pages[quarter])
        writer.add_page(demo_reader.pages[2 * quarter])
        writer.add_page(demo_reader.pages[3 * quarter])


    folder_name = "Demo"
    demo_folder = os.path.join(settings.MEDIA_ROOT, folder_name)
    os.makedirs(demo_folder, exist_ok=True)

    filename = f"final_output{sub}.pdf"

    # Full path for writing
    full_path = os.path.join(demo_folder, filename)

    # Relative path for DB
    relative_path = os.path.join(folder_name, filename)

    with open(full_path, "wb") as f:
        writer.write(f)

    return relative_path





    

def make_demo_video(source_path, full_video_path=None):

    if not os.path.isabs(source_path):
        source_path = os.path.join(settings.MEDIA_ROOT, source_path)

    if full_video_path and not os.path.isabs(full_video_path):
        full_video_path = os.path.join(settings.MEDIA_ROOT, full_video_path)

    video = VideoFileClip(source_path)

    duration = video.duration
    quarter = duration / 4
    clip_len = 20

    clip1 = video.subclipped(
        quarter,
        min(quarter + clip_len, duration)
    )

    clip2 = video.subclipped(
        2 * quarter,
        min(2 * quarter + clip_len, duration)
    )

    clip3 = video.subclipped(
        3 * quarter,
        min(3 * quarter + clip_len, duration)
    )

    demo_video = concatenate_videoclips(
        [clip1, clip2, clip3],
        method="compose"
    )

    # Reduce resolution for faster processing
    demo_video = demo_video.resized(height=720)

    folder_name = "short" if full_video_path else "Demo"

    demo_folder = os.path.join(
        settings.MEDIA_ROOT,
        folder_name
    )

    os.makedirs(demo_folder, exist_ok=True)

    filename = f"demo_{uuid.uuid4().hex}.mp4"

    full_output_path = os.path.join(
        demo_folder,
        filename
    )

    relative_output_path = os.path.join(
        folder_name,
        filename
    )

    demo_video.write_videofile(
        full_output_path,
        codec="libx264",
        audio_codec="aac",
        fps=24,
        preset="ultrafast",
        threads=8,
        logger=None
    )

    clip1.close()
    clip2.close()
    clip3.close()

    demo_video.close()
    video.close()

    return relative_output_path




def concatenate_video(v1, v2):

    video1 = VideoFileClip(v1)

    video2 = (
        VideoFileClip(v2)
        .resized(video1.size)
    )

    complete_video = concatenate_videoclips(
        [video1, video2],
        method="compose"
    )

    # Reduce resolution for faster processing
    complete_video = complete_video.resized(
        height=720
    )

    folder_name = "Demo"

    demo_folder = os.path.join(
        settings.MEDIA_ROOT,
        folder_name
    )

    os.makedirs(demo_folder, exist_ok=True)

    filename = f"demo_{uuid.uuid4().hex}.mp4"

    full_path = os.path.join(
        demo_folder,
        filename
    )

    relative_path = os.path.join(
        folder_name,
        filename
    )

    complete_video.write_videofile(
        full_path,
        codec="libx264",
        audio_codec="aac",
        fps=24,
        preset="ultrafast",
        threads=8,
        logger=None
    )

    video1.close()
    video2.close()
    complete_video.close()

    return relative_path












from PIL import Image, ImageDraw, ImageFont


def generate_certificate(
    student_name,
    course_name,
    certificate_id,
    completion_date,
    template_path,
    output_path
):
    # Open template
    image = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(image)

    # Template size
    WIDTH, HEIGHT = image.size

    # Gold color
    GOLD = (212, 175, 55)

    # ==========================================
    # Student Name Font (Auto Resize)
    # ==========================================
    student_font_size = 90

    while student_font_size > 30:
        student_font = ImageFont.truetype(
            "arialbd.ttf",
            student_font_size
        )

        bbox = draw.textbbox(
            (0, 0),
            student_name,
            font=student_font
        )

        text_width = bbox[2] - bbox[0]

        if text_width < 1100:
            break

        student_font_size -= 2

    # ==========================================
    # Course Name Font (Auto Resize)
    # ==========================================
    course_font_size = 42

    while course_font_size > 20:
        course_font = ImageFont.truetype(
            "arial.ttf",
            course_font_size
        )

        bbox = draw.textbbox(
            (0, 0),
            course_name,
            font=course_font
        )

        text_width = bbox[2] - bbox[0]

        if text_width < 1300:
            break

        course_font_size -= 1

    # ==========================================
    # Other Fonts
    # ==========================================
    info_font = ImageFont.truetype(
        "arial.ttf",
        28
    )

    # ==========================================
    # Student Name
    # ==========================================
    draw.text(
        (1000, 580),
        student_name.replace("_", " "),
        fill=GOLD,
        font=student_font,
        anchor="mm"
    )

    # ==========================================
    # Course Name
    # ==========================================
    draw.text(
        (1000, 750),
        course_name,
        fill=GOLD,
        font=course_font,
        anchor="mm"
    )

    # ==========================================
    # Completion Date
    # ==========================================
    draw.text(
        (770, 990),
        completion_date,
        fill="black",
        font=info_font
    )

    # ==========================================
    # Certificate ID
    # ==========================================
    draw.text(
        (710, 1040),
        certificate_id,
        fill="black",
        font=info_font
    )

    # Save Certificate
    image.save(output_path, quality=100)

    return output_path