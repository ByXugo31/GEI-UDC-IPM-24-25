import requests
import pytest

SERVER_URL = "http://127.0.0.1:8000"


class TestPatient:
    url = f"{SERVER_URL}/patients"
    non_existent_patient = '999999999999'

    def test_create(self):

        request = requests.post(
            self.url,
            json={
                'name': 'Name 1',
                'surname': 'Surname 1',
                'code': 'code1'
            })
        assert request.status_code == 201

        request = requests.post(
            self.url,
            json={
                'name': 'Name 2',
                'surname': 'Surname 2',
                'code': 'code2'
            })
        assert request.status_code == 201

        request = requests.post(
            self.url,
            json={
                'name': 'Name 3',
                'surname': 'Surname 3',
                'code': 'code3'
            })
        assert request.status_code == 201

    def test_find_limits(self):
        request = requests.get(f"{self.url}?start_index=0&count=3")
        assert request.status_code == 200
        data_1 = request.json()
        assert len(data_1) == 3

        request = requests.get(f"{self.url}?start_index=1&count=1")
        assert request.status_code == 200
        data_2 = request.json()
        assert len(data_2) == 1

        assert data_1[1]['id'] == data_2[0]['id']

        request = requests.get(
            f"{self.url}?start_index=999999999&count=999999")
        assert request.status_code == 200
        data_3 = request.json()
        assert len(data_3) == 0

    def test_find(self):
        request = requests.get(self.url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) >= 3

    def test_create_error(self):
        request = requests.post(
            self.url,
            json={
                'name': 'Name 1',
                'surname': 'Surname 1',
                'code': 'code1'
            })
        assert request.status_code == 409

    def test_update(self):
        code = 'code2'
        url_1 = f"{self.url}?code={code}"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert data["code"] == code

        url_2 = f"{TestPatient.url}/{data['id']}"
        request = requests.patch(
            url_2,
            json={
                'name': 'Name 222',
                'surname': 'Surname 222',
                'code': 'code2'
            })
        assert request.status_code == 204

        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert data['name'] == 'Name 222'

    def test_update_error(self):
        url = f"{self.url}/{self.non_existent_patient}"
        request = requests.patch(
            url,
            json={
                'name': 'Name 222',
                'surname': 'Surname 222',
                'code': 'code2'
            })
        assert request.status_code == 404

    def test_remove(self):
        code = 'code3'
        url_1 = f"{self.url}?code={code}"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert data["code"] == code

        url_2 = f"{self.url}/{data['id']}"
        request = requests.delete(url_2)
        assert request.status_code == 204

        request = requests.get(url_2)
        assert request.status_code == 404

    def test_remove_error(self, teardown_method):
        url = f"{self.url}/{self.non_existent_patient}"
        request = requests.delete(url)
        assert request.status_code == 404

    @pytest.fixture(scope="class")
    def teardown_method(self):
        yield "Runing teardown code"
        code = 'code1'
        url_1 = f"{self.url}?code={code}"
        request = requests.get(url_1)
        data = request.json()
        url_2 = f"{self.url}/{data['id']}"
        request = requests.delete(url_2)

        code = 'code2'
        url_1 = f"{self.url}?code={code}"
        request = requests.get(url_1)
        data = request.json()
        url_2 = f"{self.url}/{data['id']}"
        request = requests.delete(url_2)


class TestMedication:
    base_url = f"{SERVER_URL}/patients"
    non_existent_patient = '999999999999'

    @pytest.fixture(scope="class")
    def setup_teardown_method(self):
        request = requests.post(
            self.base_url,
            json={
                'name': 'Name 3',
                'surname': 'Surname 3',
                'code': 'code3'
            })
        data = request.json()
        patient_id_1 = data["id"]
        request = requests.post(
            self.base_url,
            json={
                'name': 'Name 4',
                'surname': 'Surname 4',
                'code': 'code4'
            })
        data = request.json()
        patient_id_2 = data["id"]
        yield patient_id_1, patient_id_2
        request = requests.delete(f"{self.base_url}/{patient_id_1}")
        request = requests.delete(f"{self.base_url}/{patient_id_2}")

    def test_create(self, setup_teardown_method):
        patient_id_1, patient_id_2 = setup_teardown_method
        url = f"{self.base_url}/{patient_id_1}/medications"
        request = requests.post(
            url,
            json={
                'name': 'Med1',
                'dosage': 1.0,
                'start_date': "2024-09-05",
                'treatment_duration': 10
            })
        assert request.status_code == 201
        request = requests.post(
            url,
            json={
                'name': 'Med2',
                'dosage': 1.5,
                'start_date': "2024-09-15",
                'treatment_duration': -1
            })
        assert request.status_code == 201

        url = f"{self.base_url}/{patient_id_2}/medications"
        request = requests.post(
            url,
            json={
                'name': 'Med3',
                'dosage': 0.5,
                'start_date': "2024-09-01",
                'treatment_duration': 30
            })
        assert request.status_code == 201

    def test_create_error(self):
        url = f"{self.base_url}/{self.non_existent_patient}/medications"
        request = requests.post(
            url,
            json={
                'name': 'Med1',
                'dosage': 1.0,
                'start_date': "2024-09-05",
                'treatment_duration': 10
            })
        assert request.status_code == 422

        request = requests.post(
            url,
            json={
                'name': 'Med1',
                'dosage': 1.0,
                'start_date': "09/05/2024",
                'treatment_duration': 10
            })
        assert request.status_code == 422

    def test_find(self, setup_teardown_method):
        patient_id_1, patient_id_2 = setup_teardown_method
        url = f"{self.base_url}/{patient_id_1}/medications"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2

        medication_id = data[0]["id"]
        url = f"{self.base_url}/{patient_id_1}/medications/{medication_id}"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert data["id"] == medication_id and data["name"] == "Med1" and data["patient_id"] == patient_id_1

        url = f"{self.base_url}/{patient_id_2}/medications/{medication_id}"
        request = requests.get(url)
        assert request.status_code == 404

        url = f"{self.base_url}/{self.non_existent_patient}/medications/{medication_id}"
        request = requests.get(url)
        assert request.status_code == 404

    def test_update(self, setup_teardown_method):
        patient_id_1, patient_id_2 = setup_teardown_method

        url = f"{self.base_url}/{patient_id_1}/medications"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2

        medication_id = data[0]["id"]

        url = f"{self.base_url}/{patient_id_1}/medications/{medication_id}"
        request = requests.patch(
            url,
            json={
                'name': 'Med1',
                'dosage': 2.0,
                'start_date': "2024-09-05",
                'treatment_duration': 5
            })
        assert request.status_code == 204

        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert data["id"] == medication_id and data["dosage"] == 2.0 and data["treatment_duration"] == 5

        url = f"{self.base_url}/{patient_id_2}/medications/{medication_id}"
        request = requests.patch(
            url,
            json={
                'name': 'Med1',
                'dosage': 2.0,
                'start_date': "2024-09-05",
                'treatment_duration': 5
            })
        assert request.status_code == 404

    def test_remove(self, setup_teardown_method):
        patient_id_1, patient_id_2 = setup_teardown_method

        url = f"{self.base_url}/{patient_id_1}/medications"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2

        medication_id = data[0]["id"]

        url = f"{self.base_url}/{patient_id_1}/medications/{medication_id}"
        request = requests.delete(url)
        assert request.status_code == 204

        medication_id = data[1]["id"]
        url = f"{self.base_url}/{patient_id_1}/medications/{medication_id}"
        request = requests.delete(url)
        assert request.status_code == 204

        url = f"{self.base_url}/{patient_id_2}/medications/{medication_id}"
        request = requests.delete(url)
        assert request.status_code == 404

        url = f"{self.base_url}/{patient_id_1}/medications"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 0


class TestPosology:
    base_url = f"{SERVER_URL}/patients"
    non_existent_patient = '999999999999'
    non_existent_medicine = '999999999999'
    non_existent_posology = '999999999999'

    @pytest.fixture(scope="class")
    def setup_teardown_method(self):
        request = requests.post(
            self.base_url,
            json={
                'name': 'Name 5',
                'surname': 'Surname 5',
                'code': 'code5'
            })
        data = request.json()
        patient_id = data["id"]

        url = f"{self.base_url}/{patient_id}/medications"
        request = requests.post(
            url,
            json={
                'name': 'Med1',
                'dosage': 1.0,
                'start_date': "2024-09-05",
                'treatment_duration': 10
            })
        data = request.json()
        medicine_id = data["id"]

        yield patient_id, medicine_id
        request = requests.delete(f"{self.base_url}/{patient_id}")

    def test_create(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method
        url = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies"
        request = requests.post(
            url,
            json={
                'hour': 8,
                'minute': 30
            }
        )
        assert request.status_code == 201
        request = requests.post(
            url,
            json={
                'hour': 14,
                'minute': 30
            }
        )
        assert request.status_code == 201

    def test_create_error(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method
        url = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies"
        request = requests.post(
            url,
            json={
                'hour': 60,
                'minute': 100
            }
        )
        assert request.status_code == 422

        url = f"{self.base_url}/{self.non_existent_patient}/medications/{medicine_id}/posologies"
        request = requests.post(
            url,
            json={
                'hour': 18,
                'minute': 30
            }
        )
        assert request.status_code == 422

        url = f"{self.base_url}/{patient_id}/medications/{self.non_existent_medicine}/posologies"
        request = requests.post(
            url,
            json={
                'hour': 18,
                'minute': 30
            }
        )
        assert request.status_code == 422

    def test_find(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method
        url = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2

    def test_find_error(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method
        url = f"{self.base_url}/{self.non_existent_patient}/medications/{medicine_id}/posologies"
        request = requests.get(url)
        assert request.status_code == 404
        url = f"{self.base_url}/{patient_id}/medications/{self.non_existent_medicine}/posologies"
        request = requests.get(url)
        assert request.status_code == 404

    def test_update(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method
        url_1 = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) > 0
      
        url_2 = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies/{data[0]['id']}"
        request = requests.patch(url_2, json={
            'hour': 22,
            'minute': 22
        })
        assert request.status_code == 204
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) > 0
        assert data[0]['hour'] == 22 and data[0]['minute'] == 22

    def test_update_error(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method

        url_1 = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) > 0
      
        url_2 = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies/{data[0]['id']}"
        request = requests.patch(url_2, json={
            'hour': 30,
            'minute': 66
        })
        assert request.status_code == 424

        url_2 = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies/{self.non_existent_posology}"
        request = requests.patch(url_2, json={
            'hour': 22,
            'minute': 22
        })
        assert request.status_code == 404
       
        
    

    def test_remove(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method
        url_1 = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) > 0

        posology_id = data[0]["id"]
        url_2 = f"{url_1}/{posology_id}"
        request = requests.delete(url_2)
        assert request.status_code == 204

        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 1

    def test_remove_error(self, setup_teardown_method):
        patient_id, medicine_id = setup_teardown_method
        url_1 = f"{self.base_url}/{patient_id}/medications/{medicine_id}/posologies"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) > 0
        posology_id = data[0]["id"]

        url_2 = f"{url_1}/{self.non_existent_posology}"
        request = requests.delete(url_2)
        assert request.status_code == 404

        url_3 = f"{self.base_url}/{self.non_existent_patient}/medications/{medicine_id}/posologies/{posology_id}"
        request = requests.delete(url_3)
        assert request.status_code == 404

        url_4 = f"{self.base_url}/{patient_id}/medications/{self.non_existent_medicine}/posologies/{posology_id}"
        request = requests.delete(url_4)
        assert request.status_code == 404


class TestIntake:
    base_url = f"{SERVER_URL}/patients"
    non_existent_patient = '999999999999'
    non_existent_medicine = '999999999999'
    non_existent_intake = '999999999999'

    @pytest.fixture(scope="class")
    def setup_teardown_method(self):
        request = requests.post(
            self.base_url,
            json={
                'name': 'Name 6',
                'surname': 'Surname 6',
                'code': 'code6'
            })
        data = request.json()
        patient_id_1 = data["id"]

        request = requests.post(
            self.base_url,
            json={
                'name': 'Name 7',
                'surname': 'Surname 7',
                'code': 'code7'
            })
        data = request.json()
        patient_id_2 = data["id"]

        url = f"{self.base_url}/{patient_id_1}/medications"
        request = requests.post(
            url,
            json={
                'name': 'Med1',
                'dosage': 1.0,
                'start_date': "2024-09-05",
                'treatment_duration': 10
            })
        data = request.json()
        medicine_id_1 = data["id"]

        request = requests.post(
            url,
            json={
                'name': 'Med2',
                'dosage': 0.25,
                'start_date': "2024-09-23",
                'treatment_duration': 30
            })
        data = request.json()
        medicine_id_2 = data["id"]

        url = f"{self.base_url}/{patient_id_2}/medications"
        request = requests.post(
            url,
            json={
                'name': 'Med3',
                'dosage': 2.0,
                'start_date': "2024-10-01",
                'treatment_duration': -1
            })
        data = request.json()
        medicine_id_3 = data["id"]

        yield patient_id_1, patient_id_2,  medicine_id_1, medicine_id_2, medicine_id_3
        request = requests.delete(f"{self.base_url}/{patient_id_1}")
        request = requests.delete(f"{self.base_url}/{patient_id_2}")

    def test_insert(self, setup_teardown_method):
        patient_id_1, patient_id_2, med_id_1, med_id_2, med_id_3 = setup_teardown_method

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-09-06T10:30"
            }
        )
        assert request.status_code == 201

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-09-06T14:30"
            }
        )
        assert request.status_code == 201

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-09-06T20:30"
            }
        )
        assert request.status_code == 201

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_2}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-09-24T08:30"
            }
        )
        assert request.status_code == 201

        url = f"{self.base_url}/{patient_id_2}/medications/{med_id_3}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-10-01T10:30"
            }
        )
        assert request.status_code == 201

        url = f"{self.base_url}/{patient_id_2}/medications/{med_id_3}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-10-01T15:30"
            }
        )
        assert request.status_code == 201

    def test_insert_error(self, setup_teardown_method):
        patient_id_1, _, med_id_1, _, med_id_3 = setup_teardown_method

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_3}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-09-06T10:30"
            }
        )
        assert request.status_code == 404

        url = f"{self.base_url}/{self.non_existent_patient}/medications/{med_id_3}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-09-06T10:30"
            }
        )
        assert request.status_code == 404

        url = f"{self.base_url}/{patient_id_1}/medications/{self.non_existent_medicine}/intakes"
        request = requests.post(
            url,
            json={
                "date": "2024-09-06T10:30"
            }
        )
        assert request.status_code == 404

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes"
        request = requests.post(
            url,
            json={
                "date": "no date"
            }
        )
        assert request.status_code == 422

    def test_find(self, setup_teardown_method):
        patient_id_1, patient_id_2, med_id_1, med_id_2, med_id_3 = setup_teardown_method

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 3

        url = f"{self.base_url}/{patient_id_1}/intakes"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2
        assert "intakes_by_medication" in data[0] and len(
            data[0]["intakes_by_medication"]) == 3
        assert "intakes_by_medication" in data[1] and len(
            data[1]["intakes_by_medication"]) == 1

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes?start_date=2024-09-06T09:30&end_date=2024-09-06T16:30"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes?start_date=2024-09-06T13:30"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes?end_date=2024-09-06T13:30"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 1

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes?start_date=2024-12-12T10:00"
        request = requests.get(url)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 0

    def test_find_error(self, setup_teardown_method):
        patient_id_1, _, med_id_1, _, med_id_3 = setup_teardown_method

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_3}/intakes"
        request = requests.get(url)
        assert request.status_code == 404

        url = f"{self.base_url}/{self.non_existent_patient}/medications/{med_id_3}/intakes"
        request = requests.get(url)
        assert request.status_code == 404

        url = f"{self.base_url}/{patient_id_1}/medications/{self.non_existent_medicine}/intakes"
        request = requests.get(url)
        assert request.status_code == 404

        url = f"{self.base_url}/{self.non_existent_patient}/intakes"
        request = requests.get(url)
        assert request.status_code == 404

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes?start_date=no-date&end_date=1000"
        request = requests.get(url)
        assert request.status_code == 422

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes?start_date=2000-10-20"
        request = requests.get(url)
        assert request.status_code == 422

        url = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes?end_date=1000"
        request = requests.get(url)
        assert request.status_code == 422

    def test_delete(self, setup_teardown_method):
        patient_id_1, patient_id_2, med_id_1, med_id_2, med_id_3 = setup_teardown_method

        url_1 = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 3

        intake_id = data[0]["id"]
        url_2 = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes/{intake_id}"
        request = requests.delete(url_2)
        assert request.status_code == 204

        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2

    def test_delete_error(self, setup_teardown_method):
        patient_id_1, patient_id_2, med_id_1, med_id_2, med_id_3 = setup_teardown_method

        url_1 = f"{self.base_url}/{patient_id_1}/medications/{med_id_1}/intakes"
        request = requests.get(url_1)
        assert request.status_code == 200
        data = request.json()
        assert len(data) == 2
        intake_id = data[0]["id"]

        url_2 = f"{self.base_url}/{patient_id_1}/medications/{med_id_2}/intakes/{intake_id}"
        request = requests.delete(url_2)
        assert request.status_code == 404

        url_2 = f"{self.base_url}/{patient_id_2}/medications/{med_id_1}/intakes/{intake_id}"
        request = requests.delete(url_2)
        assert request.status_code == 404

        url_2 = f"{self.base_url}/{self.non_existent_patient}/medications/{med_id_1}/intakes/{intake_id}"
        request = requests.delete(url_2)
        assert request.status_code == 404

        url_2 = f"{self.base_url}/{patient_id_1}/medications/{self.non_existent_medicine}/intakes/{intake_id}"
        request = requests.delete(url_2)
        assert request.status_code == 404

        url_2 = f"{self.base_url}/{patient_id_1}/medications/{med_id_2}/intakes/{self.non_existent_intake}"
        request = requests.delete(url_2)
        assert request.status_code == 404
