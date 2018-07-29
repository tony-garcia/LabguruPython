# -*- coding: utf-8 -*-
from __future__ import print_function

import json

from requests import HTTPError

import api
from exception import UnAuthorizeException, NotFoundException, DuplicatedException
from project import Project
from folder import Folder
from experiment import Experiment
from pojo import Session


class Labguru(object):

    def __init__(self, login, password):
        data = {
            'login': login,
            'password': password
        }

        url = api.normalise('/api/v1/sessions.json')
        response = api.request(url, data=data)
        if response.get('token') == '-1':
            raise UnAuthorizeException('Login failed! Wrong email or password')
        else:
            self.session = Session(**response)

    """
    Project API
    """
    def add_project(self, title, description=None):
        assert isinstance(title, str) and len(title) > 0, 'title is required to create a new project'

        return Project(token=self.session.token, title=title, description=description).register()

    def get_project(self, project_id):
        proj = Project(id=project_id, token=self.session.token)
        return proj.get()

    def find_project(self, name):
        return Project(token=self.session.token).list(name=name)

    def update_project(self, project_id, title, description=None):
        proj = Project(token=self.session.token, id=project_id, title=title, description=description)
        return proj.update()

    def archive_project(self):
        pass

    def list_projects(self, page_num):
        return Project(token=self.session.token).list(page_num=page_num)

    """
    Folder API
    """
    def add_folder(self, project_id, title, description=None):
        return Folder(token=self.session.token, project_id=project_id, title=title, description=description).register()

    def get_folder(self, folder_id):
        return Folder(token=self.session.token, id=folder_id).get()

    def find_folder(self, name):
        return Folder(token=self.session.token).list(name=name)

    def update_folder(self, folder_id, title, description=None):
        return Folder(token=self.session.token, id=folder_id, title=title, description=description).update()

    def list_folders(self, project_id=None, page_num=None):
        if project_id is not None:
            milestones = self.get_project(project_id=project_id).milestones
            assert isinstance(milestones, list)
            return [Folder(token=self.session.token, project_id=project_id, **milestone) for milestone in milestones]
        elif page_num is not None:
            return Folder(token=self.session.token).list(page_num=page_num)
        else:
            raise ValueError('Either project_id or page_num must be specified')

    """
    Experiment API
    """
    def add_experiment(self, project_id, folder_id, title, description=None):
        return Experiment(token=self.session.token, project_id=project_id, milestone_id=folder_id,
                          title=title, description=description).register()

    def get_experiment(self, experiment_id):
        return Experiment(token=self.session.token, id=experiment_id).get()

    def find_experiment(self, name):
        return Experiment(token=self.session.token).list(name=name)

    def update_experiment(self, experiment_id, title, description=None):
        return Experiment(token=self.session.token, id=experiment_id, title=title, description=description).update()

    def list_experiments(self, folder_id=None, page_num=None):
        if folder_id is not None:
            experiments = self.get_folder(folder_id=folder_id).experiments
            assert isinstance(experiments, list)
            return [Experiment(token=self.session.token, milestone_id=folder_id, **experiment)
                    for experiment in experiments]
        elif page_num is not None:
            return Experiment(token=self.session.token).list(page_num=page_num)
        else:
            raise ValueError('Either project_id or page_num must be specified')
