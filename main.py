from flask import Flask, render_template, request, redirect
import google.generativeai as palm


app = Flask(__name__)

palm.configure(api_key="AIzaSyCnoKn3wqil5-IG8LGRPmuEMUuFmWFU8YY")

defaults = {
    'model': 'models/text-bison-001',
    'temperature': 0.7,
    'candidate_count': 1,
    'top_k': 40,
    'top_p': 0.95,
    'max_output_tokens': 1024
}

doctor_answers = []
student_answers = []

@app.route('/')
def index():
    return render_template('doc_page.html')


@app.route('/prepare_exam', methods=['POST'])
def prepare_exam():
    num_questions = int(request.form['num_questions'])

    questions = [request.form[f'question_{i}']
                 for i in range(1, num_questions + 1)]
    answers = [request.form[f'answer_{i}']
               for i in range(1, num_questions + 1)]
    global doctor_questions, doctor_answers
    doctor_questions = questions
    doctor_answers = answers

    return redirect('/student')

@app.route('/student')
def student():
    global doctor_questions

    return render_template('stud_page.html',  questions=doctor_questions)

@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    student_answers = [request.form.get(
        f'answer_{i}', '') for i in range(1, len(doctor_answers) + 1)]
    num_correct_answers, similarity_score = compare_answers(
        doctor_answers, student_answers)

    return render_template('score.html', num_correct_answers=num_correct_answers, similarity_score=similarity_score)


def compare_answers(doctor_answers, student_answers):
    prompt = f"Do the doctor and student answers have the same meaning?\n"
    num_correct_answers = 0

    for doctor, student in zip(doctor_answers, student_answers):
        prompt += f"Doctor Answer: {doctor}\nStudent Answer: {student}\n"

        response = palm.generate_text(
            **defaults,
            prompt=prompt
        )
        similarity_score = 0

        if response.result:
            similarity_text = response.result.lower()
            if 'yes' in similarity_text:
                similarity_score = 2
                num_correct_answers += 1
            elif 'no' in similarity_text:
                similarity_score = 0

    total_questions = len(doctor_answers)
    similarity_score_percentage = (
        num_correct_answers / total_questions) * 100 if total_questions > 0 else 0

    return num_correct_answers, similarity_score_percentage



if __name__ == '__main__':
    app.run(debug=True)






















