import os
import unittest
import vtk, qt, ctk, slicer
import math
from slicer.ScriptedLoadableModule import *
import logging
import numpy as np
#
# ScalarHistogram
#

class ScalarHistogram(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "ScalarHistogram" # TODO make this more human readable by adding spaces
    self.parent.categories = ["SurfaceDistances"]
    self.parent.dependencies = []
    self.parent.contributors = ["Rachael House (Perklab, Queen's University)"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
   This module takes in a model who has scalar data and creates a histogram of the frequency of each scalar
    """
    self.parent.acknowledgementText = """
   This module takes in a model who has scalar data and creates a histogram of the frequency of each scalar
""" # replace with organization, grant and thanks.

#
# ScalarHistogramWidget
#

class ScalarHistogramWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
    #input model slector

    self.inputModelSelector = slicer.qMRMLNodeComboBox()
    self.inputModelSelector.nodeTypes = [ "vtkMRMLModelNode" ]
    self.inputModelSelector.selectNodeUponCreation = True
    self.inputModelSelector.addEnabled = False
    self.inputModelSelector.removeEnabled = False
    self.inputModelSelector.noneEnabled = False
    self.inputModelSelector.showHidden = False
    self.inputModelSelector.showChildNodeTypes = False
    self.inputModelSelector.setMRMLScene( slicer.mrmlScene )
    self.inputModelSelector.setToolTip( "Pick the input to the algorithm." )
    parametersFormLayout.addRow("Input Model: ", self.inputModelSelector)

    # Apply Button
    self.ApplyButton = qt.QPushButton("Apply")
    self.ApplyButton.enabled = True
    parametersFormLayout.addRow("", self.ApplyButton)

    # connections
    self.ApplyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)
   
    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelect()

  def cleanup(self):
    pass

  def onSelect(self):
    self.ApplyButton.enabled = self.inputModelSelector.currentNode()

  def onApplyButton(self):
    logic = ScalarHistogramLogic()
    logic.run(self.inputModelSelector.currentNode())


class ScalarHistogramLogic(ScriptedLoadableModuleLogic):

  def CreateHistogram(self, inputModel):
    #Ensuring the 
    try: 
        rangeVal = inputModel.GetPolyData().GetPointData().GetArray(0).GetRange()
    except:
        logging.error( "Error this model has no scalars")
        return
    #Creating bins for the hisogram between the max and min values of the scalar
    #rangeVal = inputModel.GetPolyData().GetPointData().GetArray(0).GetRange()
    minVal= vtk.vtkMath.Round(rangeVal[0])
    maxVal= vtk.vtkMath.Round(rangeVal[1])
    bins = []
    num = minVal
    for i in range(minVal, maxVal,5):
        bins.append(num)
        num = num + 5

    freq = []
    for i in range(len(bins)):
        freq.append(0)

    #count the frequency of value in each bins and store it in corresponding frequency array 
    total = 0
    for i in range(inputModel.GetPolyData().GetPointData().GetArray(0). GetNumberOfValues()):
        val = inputModel.GetPolyData().GetPointData().GetArray(0).GetValue(i)
        for j in range(len(bins)-1):
            if val > bins[j] and val <= bins[j+1]:
                freq[j] = freq[j] + 1
                break 

    #creating a plot in slicer
    tableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode")
    table = tableNode.GetTable()
    arrBins = vtk.vtkFloatArray()
    arrBins.SetName("Bins")
    table.AddColumn(arrBins)

    arrFreq = vtk.vtkFloatArray()
    arrFreq.SetName("Frequency")
    table.AddColumn(arrFreq)

    table.SetNumberOfRows(len(freq))
    for i in range(len(freq)):
        table.SetValue(i,1, freq[i])
        table.SetValueByName(i, "Bins", bins[i])

    plotSeriesNode1 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode")
    plotSeriesNode1.SetAndObserveTableNodeID(tableNode.GetID())
    plotSeriesNode1.SetXColumnName("Bins")
    plotSeriesNode1.SetYColumnName("Frequency")
    plotSeriesNode1.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatterBar)

    plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode")
    plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode1.GetID())
    plotChartNode.SetTitle('Histogram of Scalars')
    plotChartNode.SetXAxisTitle('Bins')
    plotChartNode.SetYAxisTitle('Frequency')

    layoutManager = slicer.app.layoutManager()
    layoutWithPlot = slicer.modules.plots.logic().GetLayoutWithPlot(layoutManager.layout)
    layoutManager.setLayout(layoutWithPlot)

    # Select chart in plot view

    plotWidget = layoutManager.plotWidget(0)
    plotViewNode = plotWidget.mrmlPlotViewNode()
    plotViewNode.SetPlotChartNodeID(plotChartNode.GetID())

   
  def run(self, inputModel):

    self.CreateHistogram(inputModel)
    return True
    
    logging.info('Processing completed')



class ScalarHistogramTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_ScalarHistogram1()

  def test_ScalarHistogram1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    self.delayDisplay('Test passed!')
