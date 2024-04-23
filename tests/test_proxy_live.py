import pytest
from requests import HTTPError
from smrtlink_client import SmrtLinkClient

class DnascSmrtLinkClient(SmrtLinkClient):

    def get_project_dict(self, id):
        '''
        Returns a dictionary of project data, or None if not found.
        Dictionary includes lists of project datasets and members.
        '''
        try:
            return self.get(f"/smrt-link/projects/{id}")
        except HTTPError as e:
            assert e.response.status_code == 404, 'Unexpected error when getting project from SMRT Link'
            return None
    
    def get_project_ids(self):
        '''Returns the ids of all projects in SMRT Link.'''
        lst = self.get("/smrt-link/projects")
        return [dct['id'] for dct in lst]


@pytest.mark.usefixtures("app_server")
def test_live_smrtlink():
    client = DnascSmrtLinkClient(
        host='localhost',
        port=8244,
        username='admin',
        password='admin',
        verify=False
    )
    project_ids = client.get_project_ids()
    assert project_ids
    assert 