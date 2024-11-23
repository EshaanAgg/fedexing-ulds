pre-zip:
	cd pre-screen && zip task.zip problem_statement.md packages.csv uld.csv

run-java:
	cd app && mvn exec:java -Dexec.mainClass="com.solver.App" -Dexec.args="10"
	python utils.py data/raw_java_choco.csv data/java_choco.csv
	python validator.py data/java_choco.csv

