import numpy as np
from csdl_alpha.utils.typing import VariableLike

import numpy as np
import xml.etree.ElementTree as ET
import sys


class Material():
    def __init__(self, name:str=None, density:VariableLike=None, 
                 compliance:VariableLike=None, 
                 strength:VariableLike=None):
        """Initialize a Material object.

        Parameters
        ----------
        name : str, optional
            The name of the material. Defaults to None.
        density : VariableLike, optional
            The density of the material. Defaults to None.
        compliance : VariableLike, optional
            The compliance matrix of the material. Defaults to None.
        strength : VariableLike, optional
            The strength matrix of the material. Defaults to None.
        """
        self.name = name
        self.density = density
        self.compliance = compliance
        self.strength = strength
        
    # https://docs.python.org/3/library/xml.etree.elementtree.html
    def import_xml(self, fname:str):
        """Import material properties from an XML file.

        Parameters
        ----------
        fname : str
            The name of the file to import from.
        """
        tree = ET.parse(fname)
        root = tree.getroot()

        self.name = root.attrib['name']

        if root.find('density') is not None: 
            self.density = float(root.find('density').text)
            
        if root.find('compliance') is not None:
            self.compliance = np.array(
                [[float(x) for x in i.text.split()] 
                for i in root.find('compliance')]
                )

        if root.find('strength') is not None:
            self.strength = np.array(
                [[float(x) for x in i.text.split()] 
                for i in root.find('strength')]
                )

    def export_xml(self, fname):
        """Export material properties to an XML file.

        Parameters
        ----------
        fname : str
            The name of the file to export to.
        """
        root = ET.Element('material')
        root.set('type', self.__class__.__name__)
        root.set('name', self.name)

        if self.density is not None:
            ET.SubElement(root, 'density').text = str(self.density)

        if self.compliance is not None:
            compliance_el = ET.SubElement(root, 'compliance')
            for row in self.compliance:
                ET.SubElement(compliance_el, 'row').text = ' '.join(map(str, row))

        if self.strength is not None:
            strength_el = ET.SubElement(root, 'strength')
            for row in self.strength:
                ET.SubElement(strength_el, 'row').text = ' '.join(map(str, row))

        tree = ET.ElementTree(root)
        if sys.version_info[1] >= 9:
            ET.indent(tree) # makes it pretty, new for Python3.9
        tree.write(fname)

def import_material(fname:str) -> Material:
    """Import material from an XML file.

    Parameters
    ----------
    fname : str
        The name of the file to import from.

    Returns
    -------
    Material
        The material object.
    """
    import caddee_materials as cm

    tree = ET.parse(fname)
    root = tree.getroot()
    name = root.attrib['name']

    mat_type = root.attrib['type']
    if mat_type == 'IsotropicMaterial':
        material = cm.IsotropicMaterial()
    elif mat_type == 'TransverseMaterial':
        material = cm.TransverseMaterial()
    else:
        material = Material()

    material.name = name
    
    if root.find('density') is not None: 
        material.density = float(root.find('density').text)
    
    if root.find('compliance') is not None:
        material.compliance = np.array(
            [[float(x) for x in i.text.split()] 
            for i in root.find('compliance')]
            )
    
    if root.find('strength') is not None:
        material.strength = np.array(
            [[float(x) for x in i.text.split()] 
            for i in root.find('strength')]
            )
    
    return material