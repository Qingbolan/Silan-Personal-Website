import React, { useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Github, Linkedin, Mail, MapPin, Phone, Globe } from 'lucide-react';

interface ContactInfo {
  type: string;
  value: string;
}

interface SocialLink {
  type: string;
  url: string;
}

interface ProjectSectionProps {
  name?: string;
  title?: string;
  current?: string;
  contacts?: ContactInfo[];
  socialLinks?: SocialLink[];
}

const ProjectSection: React.FC<ProjectSectionProps> = ({ 
  name = '', 
  title = '', 
  current = '',
  contacts = [], 
  socialLinks = [] 
}) => {
  const socialIcons = useMemo(() => {
    if (!socialLinks || !Array.isArray(socialLinks)) return [];
    return socialLinks.map(link => {
      const linkType = link.type || 'unknown';
      return {
        icon: linkType === 'github' ? <Github size={20} /> : 
              linkType === 'linkedin' ? <Linkedin size={20} /> : 
              <Globe size={20} />,
        url: link.url || '#',
        label: linkType.charAt(0).toUpperCase() + linkType.slice(1)
      };
    });
  }, [socialLinks]);

  const contactIcons = useMemo(() => {
    if (!contacts || !Array.isArray(contacts)) return [];
    return contacts.map(contact => ({
      icon: contact.type === 'email' ? <Mail size={18} /> :
            contact.type === 'phone' ? <Phone size={18} /> :
            <MapPin size={18} />,
      value: contact.value,
      type: contact.type
    }));
  }, [contacts]);

  const handleSocialClick = useCallback((url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer');
  }, []);

  return (
    <section className="relative py-16 sm:py-20">
      <div className="max-w-4xl mx-auto text-center px-4">
        {/* Name */}
        {name && (
          <motion.h1
            className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 text-theme-primary"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {name}
          </motion.h1>
        )}

        {/* Title */}
        {title && (
          <motion.h2
            className="text-lg sm:text-xl lg:text-2xl mb-6 text-gradient font-medium"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            {title}
          </motion.h2>
        )}

        {/* Current Status */}
        {current && (
          <motion.p
            className="text-base sm:text-lg mb-8 text-theme-secondary max-w-2xl mx-auto text-center"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            {current}
          </motion.p>
        )}

        {/* Contact Info */}
        {contactIcons.length > 0 && (
          <motion.div
            className="flex flex-wrap justify-center gap-6 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            {contactIcons.map((contact, index) => (
              <div key={index} className="flex items-center space-x-2 text-theme-secondary">
                {contact.icon}
                {contact.type === 'email' ? (
                  <a 
                    href={`mailto:${contact.value}`}
                    className="hover:text-theme-primary transition-colors"
                  >
                    {contact.value}
                  </a>
                ) : contact.type === 'phone' ? (
                  <a 
                    href={`tel:${contact.value}`}
                    className="hover:text-theme-primary transition-colors"
                  >
                    {contact.value}
                  </a>
                ) : (
                  <span>{contact.value}</span>
                )}
              </div>
            ))}
          </motion.div>
        )}

        {/* Social Links */}
        {socialIcons.length > 0 && (
          <motion.div
            className="flex justify-center space-x-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {socialIcons.map((social, index) => (
              <button
                key={index}
                onClick={() => handleSocialClick(social.url)}
                className="p-3 rounded-xl bg-theme-surface border border-theme-card hover:bg-theme-primary hover:text-white transition-all duration-300"
                aria-label={`Visit ${social.label}`}
              >
                {social.icon}
              </button>
            ))}
          </motion.div>
        )}
      </div>
    </section>
  );
};

export default ProjectSection; 