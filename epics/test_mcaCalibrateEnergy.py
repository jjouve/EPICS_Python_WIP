import Mca
import mcaCalibrateEnergy

m = Mca.Mca()
m.read_file('T0345.001')
mcaCalibrateEnergy.mcaCalibrateEnergy(m)
