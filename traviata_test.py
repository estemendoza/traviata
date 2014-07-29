import unittest
import os

from traviata import Traviata
from selenium import webdriver

class traviata_tests(unittest.TestCase):

    def test_ExtJS_method_calls(self):
        driver = webdriver.Firefox()
        current_dir = os.getcwd()
        driver.get("file://"+current_dir+"/test_page/index.html")
        t = Traviata.get_instance("ExtJs", driver)

        #With parameters
        cmp = t.getCmp("modules")
        self.assertIsInstance(cmp, Traviata)

        #Without paramters
        cmp = t.getVersion()
        self.assertIsInstance(cmp, Traviata)
        driver.close()

    def test_ExtJS_execute_methods_with_simple_return(self):
        driver = webdriver.Firefox()
        current_dir = os.getcwd()
        driver.get("file://"+current_dir+"/test_page/index.html")
        t = Traviata.get_instance("ExtJs", driver)
        
        cmp = t.getCmp("modules")
        size = cmp.getSize()
        self.assertEqual({ "width":300, "height":250}, { "width":size.width, "height":size.height})
        driver.close()

    def test_ExtJS_execute_methods_with_nested_calls(self):
        driver = webdriver.Firefox()
        current_dir = os.getcwd()
        driver.get("file://"+current_dir+"/test_page/index.html")
        t = Traviata.get_instance("ExtJs", driver)

        cmp = t.getCmp("modules")
        nested = cmp.getRootNode().getProxy()
        self.assertIsInstance(nested, Traviata)
        driver.close()

    def test_ExtJS_execute_methods_with_nested_calls_and_int_params(self):
        driver = webdriver.Firefox()
        current_dir = os.getcwd()
        driver.get("file://"+current_dir+"/test_page/index.html")
        t = Traviata.get_instance("ExtJs", driver)
        
        cmp = t.getCmp("modules").getRootNode().getChildAt(1)
        nested = cmp.getData()
        self.assertEquals(nested.text, "Child 2")
        cmp.set("text","Testing")
        nested = cmp.getData()
        self.assertEquals(nested.text, "Testing")
        driver.close()

    def test_ExtJS_execute_methods_with_nested_calls_and_int_params_and_columns(self):
        driver = webdriver.Firefox()

        current_dir = os.getcwd()
        driver.get("file://"+current_dir+"/test_page/index.html")
        t = Traviata.get_instance("ExtJs", driver)
        
        cmp = t.getCmp("tree_grid_cmp")
        columns = []
        for a in cmp.columns:
            columns.append(a.text)

        self.assertEquals(columns, ["Name", "Description"])

        root_node = cmp.getRootNode()
        total_childs = root_node.childNodes
        for i in range(0, len(total_childs)):
            print root_node.getChildAt(i).data.name, root_node.getChildAt(i).data.description 

        driver.close()

if __name__ == '__main__':
    unittest.main()