git pull origin next
virtualenv venv
source venv/bin/activate
python setup.py develop
cd test/src/test_pylstar/coffee_machine_example
python CoffeeMachineInferer.py 1
dot -T png coffee_machine_1.dot > coffee1.png
eog coffee1.png