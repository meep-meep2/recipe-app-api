from unittest.mock import patch         #for immitating behavior of db

from psycopg2 import OperationalError as Psycopg2Error      #possible error you can get from trying to connect to db before it is ready

from django.core.management import call_command         #helper func from django that allows you to call command by its name
from django.db.utils import OperationalError        #possible error you can get from trying to connect to db before it is ready
from django.test import SimpleTestCase          #Needed for custom test cases. Don't need db bc we are simulating the db


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):


    def test_wait_for_db_ready(self, patched_check):
        #DB already ready
        patched_check.return_value = True 

        call_command('wait_for_db')

        patched_check.assert_called_once_with(databases=['default'])

    #ORDER OF ARGUMENTS DOES MATTER!!!!!!!!!!!!! Arguments that are added in patches will be added from THE INSIDE OUT
    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        #Test waiting for db when getting operational error

        #side_effect makes it cause an exception
            #for first 2 times it should raise Psycopg2Error. The next 3 times should cause an OperationalError
            # 2 & 3 dont really matter could be any number
            #the sixth time it should return as true

        patched_check.side_effect = [Psycopg2Error] * 2 + \
            [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])


   
    # def test_wait_for_db_sleep(self, patched_sleep, patched_check):
    #     #Test waiting for db when getting operational error

    #     #side_effect makes it cause an exception
    #         #for first 2 times it should raise Psycopg2Error. The next 3 times should cause an OperationalError
    #         # 2 & 3 dont really matter could be any number
    #         #the sixth time it should return as true

    #     patched_check.side_effect = [Psycopg2Error] * 2 + \
    #         [OperationalError] * 3 + [True]

    #     call_command('wait_for_db')

    #     self.assertEqual(patched_check.call_count, 6)
    #     patched_check.assert_called_with(database=['default'])
        
        

    
