import unittest
import os
import platform
from unittest.mock import patch, MagicMock
from printer_manager import imprimir_windows, imprimir_linux, imprimir_etiquetas

class TestPrinterManager(unittest.TestCase):
    def setUp(self):
        # Crear un archivo de prueba temporal
        self.test_file = "test_print.txt"
        with open(self.test_file, "w") as f:
            f.write("Test content")

    def tearDown(self):
        # Limpiar el archivo de prueba
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    @patch('subprocess.run')
    def test_imprimir_windows(self, mock_run):
        # Probar la función de impresión en Windows
        imprimir_windows(self.test_file)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], 'start')
        self.assertEqual(args[1], '/min')
        self.assertEqual(args[3], self.test_file)

    @patch('subprocess.run')
    def test_imprimir_linux(self, mock_run):
        # Probar la función de impresión en Linux
        imprimir_linux(self.test_file)
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertEqual(args[0], 'lp')
        self.assertEqual(args[1], self.test_file)

    @patch('printer_manager.imprimir_windows')
    @patch('printer_manager.imprimir_linux')
    def test_imprimir_etiquetas_windows(self, mock_linux, mock_windows):
        # Probar la función de impresión múltiple en Windows
        with patch('platform.system', return_value='Windows'):
            imprimir_etiquetas(self.test_file, 3)
            self.assertEqual(mock_windows.call_count, 3)
            mock_linux.assert_not_called()

    @patch('printer_manager.imprimir_windows')
    @patch('printer_manager.imprimir_linux')
    def test_imprimir_etiquetas_linux(self, mock_linux, mock_windows):
        # Probar la función de impresión múltiple en Linux
        with patch('platform.system', return_value='Linux'):
            imprimir_etiquetas(self.test_file, 3)
            self.assertEqual(mock_linux.call_count, 3)
            mock_windows.assert_not_called()

    def test_imprimir_windows_error(self):
        # Probar el manejo de errores en Windows
        with patch('subprocess.run', side_effect=Exception("Test error")):
            with self.assertRaises(Exception) as context:
                imprimir_windows(self.test_file)
            self.assertIn("Error al imprimir en Windows", str(context.exception))

    def test_imprimir_linux_error(self):
        # Probar el manejo de errores en Linux
        with patch('subprocess.run', side_effect=Exception("Test error")):
            with self.assertRaises(Exception) as context:
                imprimir_linux(self.test_file)
            self.assertIn("Error al imprimir en Linux", str(context.exception))

if __name__ == '__main__':
    unittest.main() 