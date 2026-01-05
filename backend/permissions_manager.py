"""Permissions manager for educational demonstrations."""


class PermissionsManager:
    """Manages and educates about mobile app permissions."""

    ANDROID_PERMISSIONS = {
        'READ_EXTERNAL_STORAGE': {
            'name': 'Read External Storage',
            'level': 'dangerous',
            'description': 'Allows the app to read files from phone storage.',
            'risk': 'high',
            'educational_points': [
                'This permission lets apps access your documents, photos, and media.',
                'Check which apps actually need this access.',
                'Deny if you don\'t trust the app.'
            ]
        },
        'WRITE_EXTERNAL_STORAGE': {
            'name': 'Write External Storage',
            'level': 'dangerous',
            'description': 'Allows the app to create and modify files on phone storage.',
            'risk': 'high',
            'educational_points': [
                'This permission is needed for apps that create/edit files.',
                'Be careful with apps that write to storage without clear purpose.',
                'Always revoke if the app no longer needs it.'
            ]
        },
        'ACCESS_FINE_LOCATION': {
            'name': 'Fine Location',
            'level': 'dangerous',
            'description': 'Accesses precise GPS location.',
            'risk': 'high',
            'educational_points': [
                'GPS reveals your exact position to apps.',
                'Only enable for navigation and location-based services.',
                'Check settings frequently to disable unnecessary access.'
            ]
        },
        'CAMERA': {
            'name': 'Camera',
            'level': 'dangerous',
            'description': 'Allows access to the device camera.',
            'risk': 'high',
            'educational_points': [
                'Camera access can record video and photos without you knowing.',
                'Only grant to trusted apps like video chat or camera apps.',
                'Revoke if an app doesn\'t actively use it.'
            ]
        },
        'INTERNET': {
            'name': 'Internet',
            'level': 'normal',
            'description': 'Allows the app to access the network.',
            'risk': 'medium',
            'educational_points': [
                'Most apps need this for basic functionality.',
                'This permission doesn\'t reveal personal data directly.',
                'Check in-app privacy settings for data sharing.'
            ]
        }
    }

    IOS_PERMISSIONS = {
        'Photos': {
            'name': 'Photo Library Access',
            'level': 'sensitive',
            'description': 'Allows the app to access your photo library.',
            'risk': 'high',
            'educational_points': [
                'Apps can see all your photos and videos.',
                'iOS now shows "Allow Once" to limit access.',
                'Use this option unless the app frequently needs photos.'
            ]
        },
        'Location': {
            'name': 'Location Services',
            'level': 'sensitive',
            'description': 'Accesses your location data.',
            'risk': 'high',
            'educational_points': [
                'Location is tracked and can reveal your home/work.',
                'Choose "Allow While Using App" instead of "Always".',
                'Disable for apps that don\'t need real-time location.'
            ]
        },
        'Contacts': {
            'name': 'Contacts Access',
            'level': 'sensitive',
            'description': 'Allows reading your contacts.',
            'risk': 'high',
            'educational_points': [
                'Your contacts reveal your social network.',
                'Never give this to apps you don\'t fully trust.',
                'Check what contact data is actually needed.'
            ]
        }
    }

    @staticmethod
    def get_all_permissions():
        """Return all documented permissions."""
        return {
            'android': PermissionsManager.ANDROID_PERMISSIONS,
            'ios': PermissionsManager.IOS_PERMISSIONS
        }

    @staticmethod
    def get_permission(name, platform='android'):
        """Get detailed info about a specific permission."""
        perms = PermissionsManager.ANDROID_PERMISSIONS if platform == 'android' else PermissionsManager.IOS_PERMISSIONS
        return perms.get(name)

    @staticmethod
    def get_dangerous_permissions(platform='android'):
        """Get list of 'dangerous' or 'sensitive' permissions."""
        perms = PermissionsManager.ANDROID_PERMISSIONS if platform == 'android' else PermissionsManager.IOS_PERMISSIONS
        level_key = 'level' if platform == 'android' else 'level'
        dangerous_level = 'dangerous' if platform == 'android' else 'sensitive'
        return {k: v for k, v in perms.items() if v.get(level_key) == dangerous_level}

    @staticmethod
    def get_security_tips():
        """Return general security tips for storage and permissions."""
        return [
            'Regularly review and revoke app permissions you no longer need.',
            'Deny permission requests unless you understand why the app needs them.',
            'Keep your device OS and apps updated for security patches.',
            'Avoid installing apps from untrusted sources.',
            'Use device lock (PIN, pattern, face/fingerprint) to protect storage.',
            'Be wary of apps requesting multiple sensitive permissions.',
            'Delete sensitive files when you no longer need them.',
            'Use encrypted cloud storage for sensitive backups.'
        ]
