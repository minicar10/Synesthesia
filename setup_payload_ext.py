from setuptools import Extension, setup


setup(
    name="payload_ext",
    version="0.1.0",
    description="Compact metadata packet builder for Synesthesia",
    ext_modules=[
        Extension(
            "payload_ext",
            sources=["payload_ext.c"],
        )
    ],
)
