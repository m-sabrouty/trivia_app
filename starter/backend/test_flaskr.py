import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
	"""This class represents the trivia test case"""

	def setUp(self):
		"""Define test variables and initialize app."""
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name = "trivia_test"
		self.database_path = "postgresql://{}/{}".format('odoodev:samia2019@localhost:5432', self.database_name)
		setup_db(self.app, self.database_path)

		self.new_question={
			"question":"abc",
			"answer":"abc",
			"difficulty":4,
			"category":3

		}
		# binds the app to the current context
		with self.app.app_context():
			self.db = SQLAlchemy()
			self.db.init_app(self.app)
			# create all tables
			self.db.create_all()
		
	def tearDown(self):
		pass

	"""
	TODO
	Write at least one test for each test for successful operation and for expected errors.
	"""
	##beyond page
	def test_404_sent_requesting_beyond_valid_page(self):
		##questions
		res = self.client().get('/questions?page=1000')
		data = json.loads(res.data.decode('utf-8'))
		

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
	   
	##getting questions successfully
	def test_getting_questions(self):
		##questions
		res = self.client().get('/questions?page=2')
		data = json.loads(res.data.decode('utf-8'))
		self.assertEqual(data['success'], True)
		self.assertTrue(data['questions'])
		self.assertTrue(data['current_category'])
		self.assertTrue(data['categories'])
		self.assertTrue(data['total_questions'])

	##delete question
	def test_405_sent_requesting_delete_beyond_valid_questions(self):
		res = self.client().get('/questions/10000')
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 405)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'Method Not Allowed') 


	def test_deleting_question(self):
		res = self.client().delete('/questions/17')
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(data['success'], True)
		self.assertEqual(data['message'], 'Deleted Successfully') 	
		self.assertTrue(data['total_questions'])


	def test_405_deleting_question_not_found_question(self):
		res = self.client().delete('/questions/97')
		data = json.loads(res.data.decode('utf-8'))
		self.assertEqual(res.status_code, 405)
		self.assertEqual(data['success'], False)
	
	###adding question with invalid inputs
	def test_posting_question(self):
		res = self.client().post('/questions/new',json=self.new_question)
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		
	def test_405_posting_question_invalid(self):
		res = self.client().post('/questions/new',json={})
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 405)
		self.assertEqual(data['success'], False)

	def test_404_sent_requesting_question_search(self):
		res = self.client().post('/questions/search',json={})
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'resurce not found')  

	

	def test_requesting_question_search(self):
		res = self.client().post('/questions/search',json={"searchTerm":"What"})
		data = json.loads(res.data.decode('utf-8'))
		self.assertEqual(data['success'], True)
		

	def test_404_sent_requesting_question_by_category(self):
		res = self.client().get('/categories/8/questions')
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)

		self.assertEqual(data['message'], 'resurce not found')  

	def test_question_by_category(self):
		res = self.client().get('/categories/3/questions')
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 200)

		self.assertTrue(data['questions'])
		self.assertTrue(data['totalQuestions'])
		self.assertTrue(data['currentCategory'])
	# ##not sending expected data      
	def test_404_sent_requesting_quizzes(self):
		res = self.client().post('/quizzes',json={'previous_questions':[],'quiz_category':{'id':10,'type':'7amada'}})
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'resurce not found') 

	def test_requesting_quizzes(self):
		res = self.client().post('/quizzes',json={'previous_questions':[21,22],'quiz_category':{'id':2,'type':'Art'}})
		data = json.loads(res.data.decode('utf-8'))

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['questions']) 	


	# Make the tests conveniently executable
if __name__ == "__main__":
	unittest.main()