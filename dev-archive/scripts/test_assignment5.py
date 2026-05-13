"""Test script for Assignment 5: Prime Check"""
import sys
import os
import tempfile
import psycopg2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.coordinator import coordinator

def test_assignment5():
	"""Test assignment 5 with all test cases from the database."""
	
	assignment_id = 5
	
	# Read solution
	with open("solution_assignment5.py", "r") as f:
		solution_code = f.read()
	
	# Connect to database
	conn = psycopg2.connect(
		host="localhost",
		port=5432,
		database="AI3",
		user="postgres",
		password="123456"
	)
	
	# Get requirements from database
	with conn.cursor() as cur:
		cur.execute("""
			SELECT requirement_text, weight
			FROM assignment_requirements
			WHERE assignment_id=%s
		""", (assignment_id,))
		requirements = [{"requirement_text": text, "weight": float(w) if w else 1.0}
						for text, w in cur.fetchall()]
		
		# Get testcases from database
		cur.execute("""
			SELECT input_data, expected_output, score_weight
			FROM assignment_testcases
			WHERE assignment_id=%s
		""", (assignment_id,))
		testcases = [{"input_data": inp, "expected_output": out, "score_weight": float(w) if w else 1.0}
					 for inp, out, w in cur.fetchall()]
	
	conn.close()
	
	print(f"Assignment {assignment_id}: Prime Check")
	print(f"Requirements: {len(requirements)}")
	for req in requirements:
		print(f"  - {req['requirement_text']} (weight: {req['weight']})")
	
	print(f"\nTest Cases: {len(testcases)}")
	for i, tc in enumerate(testcases, 1):
		print(f"  Test {i}: Input={tc['input_data']}, Expected={tc['expected_output']}")
	
	# Create temp file
	temp_fd, temp_filepath = tempfile.mkstemp(suffix=".py", text=True)
	try:
		with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
			f.write(solution_code)
		
		print(f"\n{'='*60}")
		print("Evaluating solution...")
		print(f"{'='*60}\n")
		
		result = coordinator(
			filepath=temp_filepath,
			requirements=requirements,
			testcases=testcases
		)
		
		print(f"Syntax Score:       {result.get('syntax', {}).get('score', 0)}/20")
		print(f"Requirement Score:  {result.get('requirement', {}).get('score', 0)}/20")
		print(f"Structure Score:    {result.get('structure', {}).get('score', 0)}/20")
		print(f"Test Score:         {result.get('test', {}).get('score', 0)}/20")
		print(f"LLM Score:          {result.get('llm', {}).get('score', 0)}/20")
		
		total = result.get('total', {}).get('total_score', 0)
		print(f"\n{'='*60}")
		print(f"TOTAL SCORE: {total}/100")
		print(f"{'='*60}")
		
		if result.get('syntax', {}).get('passed'):
			print("✓ Syntax: PASSED")
		else:
			print(f"✗ Syntax: FAILED - {result.get('syntax', {}).get('error', '')}")
		
		print(f"\nTest Results:")
		test_details = result.get('test', {}).get('details', [])
		if test_details:
			if isinstance(test_details, list):
				for i, detail in enumerate(test_details, 1):
					print(f"  Test {i}: {detail}")
			else:
				print(f"  {test_details}")
	
	finally:
		os.unlink(temp_filepath)

if __name__ == "__main__":
	test_assignment5()
