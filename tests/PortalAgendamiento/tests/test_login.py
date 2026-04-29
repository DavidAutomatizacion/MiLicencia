import pytest, os


@pytest.mark.asyncio
async def test_login(logger, datos_usuario):
    logger.info("Iniciando flujo de compra de pin Colpatria")
    
    det = "eee"