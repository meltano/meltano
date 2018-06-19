import os
import markdown
import subprocess
import json

from app import db

from flask import (
  Blueprint, jsonify, request, config, current_app
)
from git import Repo

from models.projects import Project
from models.data import (
  Model, Explore, View, Dimension, Measure
)

bp = Blueprint('repos', __name__, url_prefix='/repos')

@bp.route('/', methods=['GET'])
def index():
  repo_url = Project.query.first().git_url
  # rorepo is a Repo instance pointing to the git-python repository.
  # For all you know, the first argument to Repo is a path to the repository
  # you want to work with
  repo = Repo(repo_url)
  tree = repo.heads.master.commit.tree
  sortedLkml = {'documents': [],'views': [], 'models': [], 'dashboards': []}
  for blob in tree.traverse():
    if blob.type != 'blob':
      continue
    f = blob.path
    filename, ext = os.path.splitext(f)
    file_dict = {'path': f, 'abs': blob.abspath} 
    file_dict['visual'] = filename
    file_dict['hexsha'] = blob.hexsha
    filename = filename.lower()
    if ext == '.md':
      sortedLkml['documents'].append(file_dict)
    else:
      filename, ext = os.path.splitext(filename)
      file_dict['visual'] = filename
      if ext == '.view':
        sortedLkml['views'].append(file_dict)
      if ext == '.model':
        sortedLkml['models'].append(file_dict)
      if ext == '.dashboard':
        sortedLkml['dashboards'].append(file_dict)

  return jsonify(sortedLkml)

@bp.route('/blobs/<hexsha>', methods=['GET'])
def blob(hexsha):
  repo_url = Project.query.first().git_url
  repo = Repo(repo_url)
  tree = repo.heads.master.commit.tree
  found_blob = None
  
  for blob in tree.traverse():
    if blob.hexsha == hexsha:
      found_blob = blob
      break

  filename, ext = os.path.splitext(found_blob.path)
  data = found_blob.data_stream.read().decode("utf-8")
  is_markdown = False
  if ext == '.md':
    data = markdown.markdown(data)
    is_markdown = True
  return jsonify({'blob': data, 'is_markdown': is_markdown, 'hexsha': found_blob.hexsha, 'populated': True})

@bp.route('/lint', methods=['GET'])
def lint():
  repo_url = Project.query.first().git_url
  command = ['./parser/cli.js', '--input={}/*.{{view,model}}.lkml'.format(repo_url)]
  # with open('./tmp/output.json', "w") as outfile:
  #   subprocess.call(command, stdout=outfile)
  p = subprocess.run(command, stdout=subprocess.PIPE)
  j = json.loads(p.stdout.decode("utf-8"))
  if 'errors' in j:
    return jsonify({'result': False, 'errors': j['errors']})
  else: 
    return jsonify({'result': True})

@bp.route('/update', methods=['GET'])
def db_import():
  repo_url = Project.query.first().git_url
  command = ['./parser/cli.js', '--input={}/*.{{view,model}}.lkml'.format(repo_url)]
  # with open('./tmp/output.json', "w") as outfile:
  #   subprocess.call(command, stdout=outfile)
  p = subprocess.run(command, stdout=subprocess.PIPE)
  j = json.loads(p.stdout.decode("utf-8"))
  
  
  models = j['models']
  files = j['files']
  # process views
  for file in files:
    if(file['_file_type'] == 'view'):
      file_view = file['views'][0]
      new_view_settings = {}
      if 'label' in new_view_settings:
        new_view_settings['label'] = file_view['label']
      if 'sql_table_name' in new_view_settings:
        new_view_settings['sql_table_name'] = file_view['sql_table_name']
      new_view_settings['_view'] = file_view['_view']
      new_view_settings = json.dumps(new_view_settings)
      new_view = View(new_view_settings)
      for dimension in file_view['dimensions']:
        new_dimension_settings = {}
        if 'hidden' in dimension:
          new_dimension_settings['hidden'] = dimension['hidden']
        if 'primary_key' in dimension:
          new_dimension_settings['primary_key'] = dimension['primary_key']
        if 'label' in dimension:
          new_dimension_settings['label'] = dimension['label']
        if 'type' in dimension:
          new_dimension_settings['type'] = dimension['type']
        if 'sql' in dimension:
          new_dimension_settings['sql'] = dimension['sql']
        new_dimension_settings['_dimension'] = dimension['_dimension']
        new_dimension_settings['_type'] = dimension['_type']
        new_dimension_settings['_n'] = dimension['_n']
        new_dimension_settings = json.dumps(new_dimension_settings)
        new_dimension = Dimension(new_dimension_settings)
        new_view.dimensions.append(new_dimension)
        db.session.add(new_dimension)
        new_view.dimensions.append(new_dimension)
      db.session.add(new_view)
  # process models
  for model in models:
    model_settings = {}
    if 'label' in model:
      model_settings['label'] = model['label']
    model_settings['include'] = model['include']
    model_settings['connection'] = model['connection']
    model_settings['_model'] = model['_model']
    model_settings['_type'] = model['_type']

    model_settings = json.dumps(model_settings)
    new_model = Model(model_settings)
    if len(model['explores']):
      for explore in model['explores']:
        explore_settings = {}
        if 'label' in explore:
          explore_settings['label'] = explore['label']
        if 'description' in explore:
          explore_settings['description'] = explore['description']
        explore_settings['_explore'] = explore['_explore']
        explore_settings['_type'] = explore['_type']



        explore_settings = json.dumps(explore_settings)
        new_explore = Explore(explore_settings)
        new_model.explores.append(new_explore)
        db.session.add(new_explore)
    db.session.add(new_model)
  # project = Project(name=name, git_url=git_url)
  db.session.commit()
  return jsonify({'result': True})
