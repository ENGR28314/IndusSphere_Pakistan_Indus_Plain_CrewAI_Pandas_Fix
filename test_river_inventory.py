import unittest
import data_loader

class RiverInventoryTests(unittest.TestCase):
    def test_requested_rivers_present(self):
        expected = [
            "Shigar River", "Haro River", "Korang River", "Kunhar River", "Tawi River",
            "Manawar Tawi River", "Tochi River (Gambila River)", "Chitral River (Kunar River)",
            "River Jindi (Kot & Manzari Baba)", "Panjkura River", "Bara River",
            "Lutkho River (Garam Chashma River)", "Siran River (Sirin River)", "Tangir River",
            "Astore River", "Rupal River", "Naltar River", "Hispar River",
            "Shimshal River (Shingshal River)", "Chapursan River", "Misga River", "Khunjerab River",
            "Ishkumhan River", "Yasin River", "Satpara Stream (Satpar Cho)", "Braldu River",
            "Saltoro River", "Hushe River", "Shingo River", "Rakshan River", "Beji River",
            "Anambar River", "Loralai River", "Loe Manda River", "Hakra River"
        ]
        names = set(data_loader.RIVERS["name"])
        self.assertEqual(len(expected), 35)
        self.assertTrue(set(expected).issubset(names))

    def test_new_structures_present(self):
        self.assertIn("Jinnah Barrage", set(data_loader.BARRAGES["name"]))
        self.assertIn("Kurram Tangi Dam", set(data_loader.DAMS["name"]))

    def test_new_confluences_present(self):
        expected = {"Hunza + Gilgit", "Shyok + Indus", "Ravi + Chenab"}
        self.assertTrue(expected.issubset(set(data_loader.CONFLUENCES["name"])))

if __name__ == "__main__":
    unittest.main()
