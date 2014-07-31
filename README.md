# Traviata - Javascript automation with Python and Selenium

Traviata is an adapter to handle JavaScript using Selenium. It's made with Python and the main idea is to be able to communicate Python with Javascript using python syntax and to facilitate the automation of JavaScript applications.

The ExtJS extension is included by default to be able to handle ExtJS applications but anyone can add their own custom classes to support other frameworks or to adapt it to your own JavaScript apps.

## Quick example

This is a quick example of how to use Traviata with the included ExtJS extension:

	#Open browser with webdriver
	driver = webdriver.Firefox()
	driver.get("<<point to a page with an ExtJS application>>")
	
	#Create a new Traviata object
	t = Traviata.get_instance("ExtJs", driver)
	
	#Get a component by ID
	cmp = t.getCmp("modules")
	
	#Execute any method defined in ExtJS components
	size = cmp.getSize()
	
	#Retrieve results as python objects
	print size.width
	print size.height
	
## How does it work?

Traviata translate every method or property that is specified in python and executes it on the browser using **Selenium's Webdriver**. Once it's executed, the results are parsed and converted to python objects, so that way you don't have to worry about going back and forth between Python, Selenium, Webdriver and Javascript.

## Limitations

There are some limitations due to the complexity of some JavaScript objects, like the ones present in ExtJS. So, sometimes you would ask for a method, the result would be parsed but not all JavaScript properties would be transformed to python objects or the transformation would be incomplete.

One of the main limitation is that you can't use Ext.ComponentQuery.query() method to ask for certains objects. This is because of how JSON.prune parser is implemented.

## So, what can I do?

Well, a lot of stuff, but sometimes you have to use another methods to achieve what you need. Check the examples below to understand this.

Here are some common ExtJS examples following the example above:

### Getting the properties of an object
	from pprint import pprint
	
	#Get the desired component
	cmp = t.getCmp("tree_grid_cmp")
	
	#Will show all the properties of the object
	pprint(cmp.__dict__)

### Getting items of a tree grid object

    #Assume that the tree has two columns named "Name" and "Description"
    cmp = t.getCmp("tree_grid_cmp")
    root_node = cmp.getRootNode()
    total_childs = len(root_node.childNodes)
    for i in range(0, total_childs):
            print root_node.getChildAt(i).data.name
            print root_node.getChildAt(i).data.description
            
### Getting a list of the columns of a tree grid object

    cmp = t.getCmp("tree_grid_cmp")
    columns = []
    for a in cmp.columns:
        columns.append(a.text)
        
This is just to give you an idea of what can you do with Traviata.

The goal is to create a separate page with examples of how to automate differents components, so I will be adding more examples on the future

## To Do
There a lot of stuff to implement on the ExtJS plugin like:

 * Support for objects that return a list of objects
 * Support for ComponentQuery
 * Improvements on the JSON.prune parser for complex ExtJS components
 
## Running tests
I included a small set of tests to check how Traviata works. You can find them on the `traviata_test.py` file.

These tests use a sample page inside the "test_page" folder. You also need to include your own copy of ExtJS inside "extjs" folder to be able to execute tests.
 
## Collaborators
 * **Sebastián Tello** - Refactoring and code cleanup
