import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    def paginate_questions(request, selection):
        page = request.args.get("page", 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        existent_questions = questions[start:end]

        return existent_questions

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")

        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
        return response 

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.route("/questions")
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        existent_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        the_categories = {category.id: category.type for category in categories}

        if len(existent_questions) == 0:
            abort(404)

        return jsonify(
            {
                "success": True,
                "questions": existent_questions,
                "total_questions": len(Question.query.all()),
                "categories": the_categories,
            }
        ) 

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_categories():
        page = request.args.get('page', 1, type=int)
        categories = Category.query.all()
        available_categories = {}
        for category in categories:
            available_categories[category.id] = category.type

        return jsonify({
            'success':True,
            'categories':available_categories,
            'total_categories':len(categories)
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

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def remove_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            existent_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "deleted": question_id,
                    "questions": existent_questions,
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
    def add_new_question():
        search = request.get_json()

        new_question = search.get("question", None)
        new_answer = search.get("answer", None)
        new_difficulty = search.get("difficulty", None)
        new_category = search.get("category", None)
        
        try:
            additional_question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
            additional_question.insert()

            selection = Question.query.order_by(Question.id).all()
            available_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": additional_question.id,
                    "questions": available_questions,
                    "total_questions": len(Question.query.all()),
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
    @app.route("/questions", methods=["POST"])    
    def find_questions():
        quest = request.get_json()
        search = quest.get("keyword", None)

        try:
            if search:
	            selection = Question.query.order_by(Question.id).filter(Question.question.ilike(f'%{search}%'))
	        
            available_questions = paginate_questions(request, selection)
	
            return jsonify({
                    "success": True,
                    "questions": available_questions,
                    "total_questions": len(selection.all()),
                }) 
        except:
            abort(400)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:id>/questions')
    def retrieve_questions_by_category(id):

        category = Category.query.filter_by(id=id).one_or_none()

        if (category is None):
            abort(404)
        
        selection = Question.query.filter_by(category=category.id).all()

        category_questions = paginate_questions(request, selection)

        return jsonify({'success': True,'questions': category_questions,'total_questions': len(selection),
        })

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        try:
            search = request.get_json()
            category = search.get('quiz_category')
            previous = search.get('previous_questions')
            quest = Question.id.notin_((previous))

            if category['type'] == 'click':
                questions = Question.query.filter(quest).all()
            else:
                questions = Question.query.filter_by(
                category=category['id']).filter(quest).all()
    
            question = questions[random.randrange(0, len(questions))].format() if len(questions) > 0 else None 
      
            return jsonify({
                'success': True,
                'question': question
            })
        except:
            abort(422)

    """
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False, 
            "error": 405, 
            "message": "method not allowed"
            }), 405,

    return app

