import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from  sqlalchemy.sql.expression import func, select
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__)
	setup_db(app)
	
	'''
	@TODO: DONE Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
	'''
	cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

	'''
	@TODO: Use the after_request decorator to set Access-Control-Allow DONE
	''' 
	@app.after_request
	def after_request(response):
		response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
		response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
		return response
	'''
	@TODO: Done
	Create an endpoint to handle GET requests 
	for all available categories.
	'''

	def paginate_questions(request,questions):
		page = request.args.get('page', 1, type=int)

		start =  (page - 1) * QUESTIONS_PER_PAGE

		end = start + QUESTIONS_PER_PAGE

		questions= [q.format() for q in questions]

		current_questions = questions[start:end]
		return current_questions

	@app.route('/categories',methods=['GET'])
	def retrieve_all_cats():
		category={}
		cat_all= [c.format() for c in Category.query.order_by(Category.id).all()]
		for c in cat_all:
			category[str(c['id'])]=c['type']
		if len(category) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'categories': category,
		})



	'''
	@TODO: Done
	Create an endpoint to handle GET requests for questions, 
	including pagination (every 10 questions). 
	This endpoint should return a list of questions, 
	number of total questions, current category, categories. 
	TEST: At this point, when you start the application
	you should see questions and categories generated,
	ten questions per page and pagination at the bottom of the screen for three pages.
	Clicking on the page numbers should update the questions. 
	'''
	@app.route('/questions',methods=['GET'])
	def retrieve_all_questions():

		questions = Question.query.order_by(Question.id).all()
		categories=[c.format() for c in Category.query.order_by(Category.id).all()]
		current_questions = paginate_questions(request, questions)
		current_categ_ids=[s for s in set([q['category'] for q in current_questions])]
		current_category= Category.query.filter(Category.id.in_(current_categ_ids)).all()
		if len(current_questions) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'questions':  current_questions,
			'current_category':[c.format() for c in current_category],
			'categories':categories,
			'total_questions': len(Question.query.all())
			
		})



	'''
	@TODO: Done
	Create an endpoint to DELETE question using a question ID. 

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''
	@app.route('/questions/<int:question_id>',methods=['Delete'])
	def delete_question(question_id):
		try:
			question_to_be_deleted= Question.query.get(question_id)
			question_to_be_deleted.delete()
			return jsonify({
				'success': True,
				'message':'Deleted Successfully',
				'total_questions': len(Question.query.all())

			})
		except:
			abort(405)  

	'''
	@TODO: Done
	Create an endpoint to POST a new question, 
	which will require the question and answer text, 
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab, 
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.  
	'''
	@app.route('/questions/new',methods=['POST'])
	def question_create():
		body=request.get_json()
		new_ques=body.get('question',None)
		new_ans=body.get('answer',None)
		new_diff=body.get('difficulty',None)
		new_cat=body.get('category',None)
		try:
			new_question=Question(question=new_ques,answer=new_ans,difficulty=new_diff,category=new_cat)
			new_question.insert()
			
			return jsonify({
				'success': True,
				'message':'Question Added Successfully',

			})
		except:
			abort(405) 
	'''
	@TODO: Done
	Create a POST endpoint to get questions based on a search term. 
	It should return any questions for whom the search term 
	is a substring of the question. 

	TEST: Search by any phrase. The questions list will update to include 
	only question that include that string within their question. 
	Try using the word "title" to start. 
	'''
	@app.route('/questions/search',methods=['POST'])
	def question_search():
		body=request.get_json()
		searchTerm=body.get('searchTerm',None)
	 
	
		try:
			result=Question.query.filter(Question.question.ilike('%'+searchTerm +'%'))
			if result:
				search_count=result.count()
				
				question_results=result.all()
		 
				current_questions = paginate_questions(request, question_results)
		
				current_categ_ids=[s for s in set([q['category'] for q in current_questions])]
				
				current_category= Category.query.filter(Category.id.in_(current_categ_ids)).all()
				categs=[c.format() for c in current_category]
				
				return jsonify({
					'success': True,
					'questions':[q['question'] for q in current_questions],
					'totalQuestions':search_count,
					'currentCategory':categs,
				})
		except:
			abort(404) 
	'''
	@TODO: DONE
	Create a GET endpoint to get questions based on category. 

	TEST: In the "List" tab / main screen, clicking on one of the 
	categories in the left column will cause only questions of that 
	category to be shown. 
	'''
	@app.route('/categories/<int:cat_id>/questions',methods=['GET'])
	def question_get_by_category(cat_id):
		
		try:
			result=Question.query.filter_by(category=cat_id).all()
			currentCategory=Category.query.get(cat_id)
			if result:
				question_results=[res.format() for res in result]
			 
			return jsonify({
				'success': True,
				'questions':[q['question'] for q in question_results],
				'totalQuestions':len(result),
				'currentCategory':currentCategory.type

			})
		except:
			abort(404) 

	'''
	@TODO: DONE
	Create a POST endpoint to get questions to play the quiz. 
	This endpoint should take category and previous question parameters 
	and return a random questions within the given category, 
	if provided, and that is not one of the previous questions. 

	TEST: In the "Play" tab, after a user selects "All" or a category,
	one question at a time is displayed, the user is allowed to answer
	and shown whether they were correct or not. 
	'''
	@app.route('/quizzes',methods=['POST'])
	def quizzes():
		body=request.get_json()
		## list of ques ids 
		previous_questions=body.get('previous_questions',None)   
		##category
		quiz_category=body.get('quiz_category',None)
		quiz_category_id=quiz_category['id']
		
		try:
			if quiz_category_id!=0:
				questions=Question.query.filter(Question.category==quiz_category_id).\
				filter(~Question.id.in_(previous_questions)).order_by(func.random()).all()
			
			elif quiz_category_id==0:
				questions=Question.query.filter(~Question.id.in_(previous_questions)).order_by(func.random()).all()
			
			
			if len(questions)>0:
				question_res=[q.format() for q in questions ]
		
			return jsonify({
				'success': True,
				'questions':question_res,
			})
		except:
			abort(404)   
	'''
	@TODO: Done
	Create error handlers for all expected errors 
	including 404 and 422. 
	'''
	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
						'success':False,
						'error':404,
						'message':'resurce not found'
				}) ,404
	@app.errorhandler(422)
	def unproccessable(error):
		return jsonify({
						'success':False,
						'error':422,
						'message':'unproccessable'
				}) ,422  
	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
						'success':False,
						'error':400,
						'message':'Bad Request'
				}) ,400

	@app.errorhandler(500)
	def server_error(error):
		return jsonify({
						'success':False,
						'error':500,
						'message':'Internal Server Error'
				}) ,500

	@app.errorhandler(405)
	def not_allaowd(error):
		return jsonify({
						'success':False,
						'error':405,
						'message':'Method Not Allowed'
				}) ,405  



	return app

		