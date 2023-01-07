#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, os

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        doc = app.activeDocument
        products = doc.products
        product = products.itemByProductType('CAMProductType')

        # check if the document has a CAMProductType.  I will not if there are no CAM operations in it.
        if product == None:
            ui.messageBox('There are no CAM operations in the active document.  This script requires the active document to contain at least one CAM operation.',
                            'No CAM Operations Exist',
                            adsk.core.MessageBoxButtonTypes.OKButtonType,
                            adsk.core.MessageBoxIconTypes.CriticalIconType)
            return

        cam = adsk.cam.CAM.cast(product)

        # specify the program name, post configuration to use and a folder destination for the nc file
        parentFolder = doc.dataFile.parentFolder.name
        docName = doc.name.replace(" ", "_")
        programName = '101'
        outputPath = "/Users/tomasspacil/Desktop/CAM/" + parentFolder + "/" + docName
        outputFolder = outputPath

        # set the post configuration to use based on Operation Type of the first Setup
        firstSetupOperationType = cam.setups.item(0).operationType
        if firstSetupOperationType == adsk.cam.OperationTypes.MillingOperation:
            postConfig = os.path.join(cam.personalPostFolder, 'heidenhain.cps') 
        elif firstSetupOperationType == adsk.cam.OperationTypes.TurningOperation:
            postConfig = os.path.join(cam.genericPostFolder, 'fanuc turning.cps') 
        elif firstSetupOperationType == adsk.cam.OperationTypes.JetOperation:
            postConfig = cam.genericPostFolder + '/' + 'omax.cps' 

        # specify the NC file output units
        units = adsk.cam.PostOutputUnitOptions.DocumentUnitsOutput

        # create the postInput object
        postInput = adsk.cam.PostProcessInput.create(programName, postConfig, outputFolder, units)
        postInput.isOpenInEditor = False

        # create the post properties
        postProperties = adsk.core.NamedValues.create()
        # create the disable sequence number property
        disableSequenceNumbers = adsk.core.ValueInput.createByBoolean(False)
        postProperties.add("showSequenceNumbers", disableSequenceNumbers)
        # add the post properties to the post process input
        postInput.postProperties = postProperties

        # set the value of scenario to 1, 2 or 3 to post all, post the first setup, or post only the first operation of the first setup.

        ui.messageBox('Nyní vygeneruji všechny programy do složek dle operací.')
        setups = cam.setups
        setupNum = 1
        for setup in setups:
            programNum = 1
            operations = setup.allOperations
            postInput.outputFolder = outputPath + "/" + setup.name
            for operation in operations:
                if operation.hasToolpath == True:
                    postInput.programName = str(setupNum) + "0" + str(programNum)
                    cam.postProcess(operation, postInput)
                    programNum += 1
                else:
                    ui.messageBox('Nenalezeny dráhy k vygenerování!')
            setupNum += 1
            

        ui.messageBox('Generování hotovo. Zapsáno do:\n"' + os.path.join(outputFolder, programName) + '.h"') 

        # open the output folder in Finder on Mac or in Explorer on Windows
        if (os.name == 'posix'):
            os.system('open "%s"' % outputFolder)
        elif (os.name == 'nt'):
            os.startfile(outputFolder)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))