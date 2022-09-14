import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys
sys.path.insert(0, '/backend/models.py')
from models import *
# from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    # Set Up the CORS middleware. Allow '*' for origins.
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    # Function created to manage the addition of CORS headers
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')

        return response
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """


    def pagination(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        formatted_questions = [question.format() for question in selection]
        present_questions = formatted_questions[start:end]

        return present_questions
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/category')
    def categories():
        # TODO: replace with real data returned from querying the database
        categories = Category.query.order_by(Category.id).all()
        categoryList= {}
        if len(categories) == 0:
            abort(404)
        for category in categories:
            categoryList[category.id] = category.type
        return jsonify({
            'categories': categoryList,
            'success': True
            
        })

        

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def questions():
        selection = Question.query.order_by(Question.id).all()
        present_questions = pagination(request, selection)

        categories = Category.query.order_by(Category.type).all()

        if len(present_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': present_questions,
            'total_questions': len(selection),
            'categories': {category.id: category.type for category in categories},
            'present_category': None
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category',  None)
        searchTerm = body.get('searchTerm', None)

        try:
            if searchTerm:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike("%{}%".format(searchTerm))
                )
                present_questions = pagination(request, selection)

                return jsonify(
                    {
                        "success": True,
                        "questions": present_questions,
                        "total_questions": len(selection.all()),
                    }
                )
            else:
                new_question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
                new_question.insert()

                selection = Question.query.order_by(Question.id).all()
                present_questions = pagination(request, selection)

                return jsonify(
                    {
                        "success": True,
                        'question_created': new_question.question,
                        'created': new_question.id,
                        'questions': present_questions,
                        'total_questions': len(Question.query.all())
                    }
                )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/category/<int:category_id>/questions')
    def category_based_questions(category_id):
        category = Category.query.filter_by(id=category_id).one_or_none()
        if category is None:
            abort(404)
        try:
            questions = Question.query.filter_by(category=category.id).all()
            present_questions = pagination(request, questions)

            return jsonify({
                'success': True,
                'total_questions': len(questions),
                'present_category': category.id,
                'questions': present_questions
            })

        except:
            abort(400)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/play', methods=['POST'])
    def play():
        try:
            body = request.get_json()
            past_questions = body.get('previous_questions', None)
            category = body.get('quiz_category', None)
            category_id = category['id']
            upcoming_question = None
            
            if category_id != 0:
                questions = Question.query.filter_by(category=category_id).filter(Question.id.notin_((past_questions))).all()    
            else:
                questions = Question.query.filter(Question.id.notin_((past_questions))).all()
            if len(questions) > 0:
                upcoming_question = random.choice(questions).format()
            return jsonify({
                'question': upcoming_question,
                'success': True,
            })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(405)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 405, "message": "method not allowed"}),
            405,
        )
    return app

