import numpy as np
from csdl_alpha.utils.typing import VariableLike
import numpy as np
from ..material import Material
import csdl_alpha as csdl
from csdl_alpha.utils.inputs import variablize


class IsotropicMaterial(Material):
    def __init__(self, name:str=None, density:VariableLike=None,
                 E:VariableLike=None, nu:VariableLike=None, G:VariableLike=None,
                 Ft:VariableLike=None, Fc:VariableLike=None, F12:VariableLike=None):
        """Initialize an isotropic material object.

        Parameters
        ----------
        name : str, optional
            The name of the material. Defaults to None.
        density : VariableLike, optional
            The density of the material. Defaults to None.
        E : VariableLike, optional
            The Young's modulus of the material. Defaults to None.
        nu : VariableLike, optional
            The Poisson's ratio of the material. Defaults to None.
        G : VariableLike, optional
            The shear modulus of the material. Defaults to None.
        Ft : VariableLike, optional
            The tensile strength of the material. Defaults to None.
        Fc : VariableLike, optional
            The compressive strength of the material. Defaults to None.
        F12 : VariableLike, optional
            The shear strength of the material. Defaults to None.
        """
        super().__init__(name=name, density=density)

        if E is None and nu is None and G is None:
            pass
        else:
            self.set_compliance(E=E, nu=nu, G=G)
        if Ft is None and Fc is None and F12 is None:
            pass
        else:
            if Ft is None or Fc is None or F12 is None:
                raise Exception('Material strength properties are uderdefined')
            self.set_strength(Ft=Ft, Fc=Fc, F12=F12)


    def set_compliance(self, E = None, nu = None, G = None):
            if not None in [E, nu]:
                pass
            elif not None in [G, nu]:
                E = G*2*(1+nu)
            elif not None in [E, G]:
                nu = E/(2*G)-1
            else:
                raise Exception('Material properties are uderdefined')
            
            if any(isinstance(x, csdl.Variable) for x in [E, nu, G]):
                E = variablize(E).reshape((1,1))
                nu = variablize(nu).reshape((1,1))
                _nu = (-nu).reshape((1,1))
                o_nu = (1+nu).reshape((1,1))
                z = csdl.Variable(value=0, shape=(1,1))
                o = csdl.Variable(value=1, shape=(1,1))
                self.compliance = 1/E*csdl.blockmat(
                    [[o, _nu, _nu, z, z, z],
                    [_nu, o, _nu, z, z, z],
                    [_nu, _nu, o, z, z, z],
                    [z, z, z, o_nu, z, z],
                    [z, z, z, z, o_nu, z],
                    [z, z, z, z, z, o_nu]]
                )
            else:
                self.compliance = 1/E*np.array(
                    [[1, -nu, -nu, 0, 0, 0],
                    [-nu, 1, -nu, 0, 0, 0],
                    [-nu, -nu, 1, 0, 0, 0],
                    [0, 0, 0, 1+nu, 0, 0],
                    [0, 0, 0, 0, 1+nu, 0],
                    [0, 0, 0, 0, 0, 1+nu]]
                )

    def get_constants(self):
        """Calculate material properties from compliance matrix.

        Returns
        -------
        tuple
            A tuple containing the following material properties:
            - E: Young's modulus
            - nu: Poisson's ratio
            - G: Shear modulus
        """
        E = 1/self.compliance[0,0]
        nu = -self.compliance[0,1]*E
        G = E/(2*(1+nu))
        return E, nu, G

    def from_compliance(self):
        """Depricated - use get_constants()"""
        return self.get_constants()

    def set_strength(self, Ft, Fc, F12):
        """Set the strength properties of the material."""
        if any(isinstance(x, csdl.Variable) for x in [Ft, Fc, F12]):
            Ft = variablize(Ft)
            Fc = variablize(Fc)
            F12 = variablize(F12)
            self.strength = csdl.blockmat([[Ft, Ft, Ft],[Fc, Fc, Fc],[F12, F12, F12]])
        else:
            self.strength = np.array([[Ft, Ft, Ft],[Fc, Fc, Fc],[F12, F12, F12]])


def test_isotropic_numpy():
    E = 1e7
    nu = 0.3
    G = E/(2*(1+nu))

    mat = IsotropicMaterial(E=E, nu=nu)
    E_, nu_, G_ = mat.get_constants()
    assert np.isclose(E, E_)
    assert np.isclose(nu, nu_)
    assert np.isclose(G, G_)

    mat = IsotropicMaterial(G=G, nu=nu)
    E_, nu_, G_ = mat.get_constants()
    assert np.isclose(E, E_)
    assert np.isclose(nu, nu_)
    assert np.isclose(G, G_)

    mat = IsotropicMaterial(E=E, G=G)
    E_, nu_, G_ = mat.get_constants()
    assert np.isclose(E, E_)
    assert np.isclose(nu, nu_)
    assert np.isclose(G, G_)

def test_isotropic_csdl():
    rec = csdl.Recorder(inline=True)
    rec.start()

    E = csdl.Variable(value=1e7)
    nu = csdl.Variable(value=0.3)
    G = E/(2*(1+nu))

    mat = IsotropicMaterial(E=E, nu=nu)
    E_, nu_, G_ = mat.get_constants()
    assert np.isclose(E.value, E_.value)
    assert np.isclose(nu.value, nu_.value)
    assert np.isclose(G.value, G_.value)

    mat = IsotropicMaterial(G=G, nu=nu)
    E_, nu_, G_ = mat.get_constants()
    assert np.isclose(E.value, E_.value)
    assert np.isclose(nu.value, nu_.value)
    assert np.isclose(G.value, G_.value)

    mat = IsotropicMaterial(E=E, G=G)
    E_, nu_, G_ = mat.get_constants()
    assert np.isclose(E.value, E_.value)
    assert np.isclose(nu.value, nu_.value)
    assert np.isclose(G.value, G_.value)