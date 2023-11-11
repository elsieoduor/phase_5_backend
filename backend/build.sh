# exit on error

set -o errexit

pip install -r requirements.txt

python3 manage.py commectstatic --no-input
python3 manage.py migrate