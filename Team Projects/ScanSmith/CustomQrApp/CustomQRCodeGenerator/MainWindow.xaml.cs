using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using Microsoft.Win32;
using QRCoder;

namespace CustomQRCodeGenerator;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    private byte[]? _latestQrCodeBytes;

    public MainWindow()
    {
        InitializeComponent();
    }

    private void OnParametersChanged(object sender, EventArgs e)
    {
        if (TxtInput == null || CmbEcc == null || CmbDarkColor == null || CmbLightColor == null)
            return;

        string textToEncode = TxtInput.Text;

        if (string.IsNullOrWhiteSpace(textToEncode))
        {
            ImgPreview.Source = null;
            TxtPlaceholder.Visibility = Visibility.Visible;
            _latestQrCodeBytes = null;
            return;
        }

        TxtPlaceholder.Visibility = Visibility.Collapsed;
        GenerateQRCode(textToEncode);
    }

    private void GenerateQRCode(string text)
    {
        try
        {
            QRCodeGenerator.ECCLevel eccLevel = CmbEcc.SelectedIndex switch
            {
                0 => QRCodeGenerator.ECCLevel.L,
                1 => QRCodeGenerator.ECCLevel.M,
                2 => QRCodeGenerator.ECCLevel.Q,
                3 => QRCodeGenerator.ECCLevel.H,
                _ => QRCodeGenerator.ECCLevel.M
            };

            byte[] darkColor = GetSelectedColor(CmbDarkColor.SelectedIndex, true);
            byte[] lightColor = GetSelectedColor(CmbLightColor.SelectedIndex, false);

            using var qrGenerator = new QRCodeGenerator();
            using var qrCodeData = qrGenerator.CreateQrCode(text, eccLevel);
            using var qrCode = new PngByteQRCode(qrCodeData);

            _latestQrCodeBytes = qrCode.GetGraphic(20, darkColor, lightColor);
            ImgPreview.Source = ConvertBytesToBitmapImage(_latestQrCodeBytes);
        }
        catch (Exception ex)
        {
            MessageBox.Show($"Error generating QR code: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private static byte[] GetSelectedColor(int index, bool isDarkColor)
    {
        if (isDarkColor)
        {
            return index switch
            {
                1 => new byte[] { 26, 54, 93, 255 },
                2 => new byte[] { 20, 83, 45, 255 },
                3 => new byte[] { 153, 27, 27, 255 },
                _ => new byte[] { 0, 0, 0, 255 }
            };
        }

        return index switch
        {
            1 => new byte[] { 229, 231, 235, 255 },
            2 => new byte[] { 0, 0, 0, 0 },
            _ => new byte[] { 255, 255, 255, 255 }
        };
    }

    private static BitmapImage ConvertBytesToBitmapImage(byte[] bytes)
    {
        if (bytes == null || bytes.Length == 0)
            return new BitmapImage();

        var image = new BitmapImage();
        using var stream = new MemoryStream(bytes);
        image.BeginInit();
        image.CreateOptions = BitmapCreateOptions.PreservePixelFormat;
        image.CacheOption = BitmapCacheOption.OnLoad;
        image.UriSource = null;
        image.StreamSource = stream;
        image.EndInit();
        image.Freeze();
        return image;
    }

    private void BtnExport_Click(object sender, RoutedEventArgs e)
    {
        if (_latestQrCodeBytes == null)
        {
            MessageBox.Show("Please generate a QR code first by typing in some data.", "Warning", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var saveFileDialog = new SaveFileDialog
        {
            Filter = "PNG Image (*.png)|*.png",
            FileName = "CustomQRCode.png"
        };

        if (saveFileDialog.ShowDialog() == true)
        {
            File.WriteAllBytes(saveFileDialog.FileName, _latestQrCodeBytes);
            MessageBox.Show("QR Code saved successfully!", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }
}
