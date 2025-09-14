import { useTheme } from '../components/ThemeContext';

const Footer = () => {
  const { isDarkMode} = useTheme();
  return (
    <footer className={`text-center mt-12 text-sm ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
      <p>&copy; {new Date().getFullYear()} Silan Hu. All rights reserved.</p>
    </footer>
  );
};

export default Footer;