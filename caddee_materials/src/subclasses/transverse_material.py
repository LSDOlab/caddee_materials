import numpy as np
from csdl_alpha.utils.typing import VariableLike
import numpy as np
from ..material import Material

class TransverseMaterial(Material):
    def __init__(self, name:str=None, density:VariableLike=None,
                EA:VariableLike=None, ET:VariableLike=None, vA:VariableLike=None, vT:VariableLike=None, GA:VariableLike=None,
                F1t:VariableLike=None, F1c:VariableLike=None, F2t:VariableLike=None, F2c:VariableLike=None, F12:VariableLike=None, F23:VariableLike=None):
        """Initialize a transverse material object.

        Parameters
        ----------
        name : str, optional
            The name of the material. Defaults to None.
        density : VariableLike, optional
            The density of the material. Defaults to None.
        EA : VariableLike, optional
            Young's modulus in the axial direction. Defaults to None.
        ET : VariableLike, optional
            Young's modulus in the transverse direction. Defaults to None.
        vA : VariableLike, optional
            Poisson's ratio in the axial direction. Defaults to None.
        vT : VariableLike, optional
            Poisson's ratio in the transverse direction. Defaults to None.
        GA : VariableLike, optional
            Shear modulus in the axial direction. Defaults to None.
        F1t : VariableLike, optional
            Tensile strength in the 1 direction. Defaults to None.
        F1c : VariableLike, optional
            Compressive strength in the 1 direction. Defaults to None.
        F2t : VariableLike, optional
            Tensile strength in the 2 direction. Defaults to None.
        F2c : VariableLike, optional
            Compressive strength in the 2 direction. Defaults to None.
        F12 : VariableLike, optional
            Shear strength in the 1-2 plane. Defaults to None.
        F23 : VariableLike, optional
            Shear strength in the 2-3 plane. Defaults to None.
        """
        super().__init__(name=name, density=density)
        if EA is not None or ET is not None or vA is not None or vT is not None or GA is not None:
            self.set_compliance(EA=EA, ET=ET, vA=vA, GA=GA, vT=vT, GT=None)

                 


    # TODO: add csdl input support
    def set_compliance(self, EA:float, ET:float, vA:float, GA:float, vT:float=None, GT:float=None):
        """Set the compliance matrix for the material.

        This method calculates and sets the compliance matrix based on the given material properties.

        Parameters
        ----------
        EA : float
            Young's modulus in the axial direction.
        ET : float
            Young's modulus in the transverse direction.
        vA : float
            Poisson's ratio in the axial direction.
        GA : float
            Shear modulus in the axial direction.
        vT : float, optional
            Poisson's ratio in the transverse direction. Default is None.
        GT : float, optional
            Shear modulus in the transverse direction. Default is None.

        Raises
        ------
        Exception
            If the material properties are not sufficient to define the compliance matrix.
        """
        if vT is not None and GT is None:
            GT = ET / (2 * (1 + vT))  # = G23
        elif GT is not None and vT is None:
            vT = ET / (2 * GT) - 1
        else:
            raise Exception('Material is underdefined')

        self.compliance = np.array(
            [[1 / ET, -vT / ET, -vA / EA, 0, 0, 0],
             [-vT / ET, 1 / ET, -vA / EA, 0, 0, 0],
             [-vA / EA, -vA / EA, 1 / EA, 0, 0, 0],
             [0, 0, 0, 1 / GA, 0, 0],
             [0, 0, 0, 0, 1 / GA, 0],
             [0, 0, 0, 0, 0, 1 / GT]]
        )

    def get_constants(self):
        """Calculate material properties from compliance matrix.

        Returns
        -------
        tuple
            A tuple containing the following material properties:
            - EA: Young's modulus in the axial direction
            - ET: Young's modulus in the transverse direction
            - vA: Poisson's ratio in the axial direction
            - vT: Poisson's ratio in the transverse direction
            - GA: Shear modulus
        """
        ET = 1/self.compliance[0,0]
        EA = 1/self.compliance[2,2]
        vT = -self.compliance[1,0]*ET
        vA = -self.compliance[2,0]*EA
        GA = 1/self.compliance[3,3]        
        return EA, ET, vA, vT, GA

    def from_compliance(self):
        """Depricated - use get_constants()
        
        Calculate material properties from compliance matrix.

        Returns
        -------
        tuple
            A tuple containing the following material properties:
            - EA: Young's modulus in the axial direction
            - ET: Young's modulus in the transverse direction
            - vA: Poisson's ratio in the axial direction
            - vT: Poisson's ratio in the transverse direction
            - GA: Shear modulus
        """
        return self.get_constants()

    def set_strength(self, F1t, F1c, F2t, F2c, F12, F23):
        self.strength = np.array(
            [[F1t, F2t, F2t],
            [F1c, F2c, F2c],
            [F12, F12, F23]]
            )
        

