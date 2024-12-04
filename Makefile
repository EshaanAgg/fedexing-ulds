cnt=20

pre-zip:
	cd pre-screen && zip task.zip problem_statement.md packages.csv uld.csv

run-java:
	cd app && mvn exec:java -Dexec.mainClass="com.solver.App" -Dexec.args="$(cnt)"
	python utils.py data/raw_java_choco.csv data/java_choco.csv
	python validator.py data/java_choco.csv

start:
	cd viz && npm run dev &
 	conda activate fedex && cd server && uvicorn main:app --reload