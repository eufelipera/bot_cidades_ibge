# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *
from botcity.web.util import element_as_select
from botcity.web.parsers import table_to_dict
from webdriver_manager.firefox import GeckoDriverManager
from botcity.plugins.excel import BotExcelPlugin


# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False

excel = BotExcelPlugin()
excel.add_row(['Cidade', 'População'])
def main():
    # Runner passes the server url, the id of the task being executed,
    # the access token and the parameters that this task receives (when applicable).
    maestro = BotMaestroSDK.from_sys_args()
    # ## Fetch the BotExecution with details from the task, including parameters
    execution = maestro.get_execution()

    print(f"Task ID is: {execution.task_id}")
    print(f"Task Parameters are: {execution.parameters}")

    bot = WebBot()

    # Configure whether or not to run on headless mode
    bot.headless = False

    # Uncomment to change the default Browser to Firefox
    bot.browser = Browser.FIREFOX

    # Uncomment to set the WebDriver path
    bot.driver_path = GeckoDriverManager().install()
    # Opens the BotCity website.
    bot.browse("https://buscacepinter.correios.com.br/app/faixa_cep_uf_localidade/index.php")

    bot.wait(1000)
    bot.maximize_window()

    # estrutura xpath: //tag[@atributo='valor']
    drop_uf = element_as_select(bot.find_element("//select[@id='uf']", By.XPATH))
    drop_uf.select_by_value("SP")

    btn_pesquisar = bot.find_element("//button[@id='btn_pesquisar']", By.XPATH)
    btn_pesquisar.click()

    bot.wait(3000)

    table_dados = bot.find_element("//table[@id='resultado-DNEC']", By.XPATH)
    table_dados = table_to_dict(table=table_dados)

    bot.navigate_to("https://cidades.ibge.gov.br/brasil/sp/panorama")
    cidade_anterior = ''
    contador = 1
    for cidade in table_dados:
        if contador <= 5: #limitador temporario
            str_Cidade = cidade["localidade"]

            if str_Cidade == cidade_anterior:
                continue

            campo_pesquisa = bot.find_element("//input[@placeholder='O que você procura?']", By.XPATH)
            campo_pesquisa.send_keys(str_Cidade)

            #utilizando xpath com ancora
            opcao_cidade = bot.find_element(f"//a[span[contains(text(), '{str_Cidade}')] and span[contains(text(), 'SP')]]", By.XPATH)
            bot.wait(1000)
            opcao_cidade.click()

            bot.wait(2000)

            populacao = bot.find_element('//div[@class="indicador__valor"]', By.XPATH)
            #capturando atributo text do elemento populacao
            str_populacao = populacao.text


            print(str_Cidade, str_populacao)

            #escrevendo no excel na memoria
            excel.add_row([str_Cidade, str_populacao])
            maestro.new_log_entry(activity_label='CIDADES', values={'CIDADE': f'{str_Cidade}', 'POPULACAO': f'{str_populacao}'})

            cidade_anterior = str_Cidade
            contador = contador + 1
        else:
            print('Numero de cidades já alcançada.')
            break
    #grava excel que estava na memoria.
    excel.write(r'C:\Users\felip\OneDrive\Documentos\Python\intensivo_botcity\info_cidades.xlsx')
    # Implement here your logic...
    ...

    # Wait 3 seconds before closing
    bot.wait(5000)

    # Finish and clean up the Web Browser
    # You MUST invoke the stop_browser to avoid
    # leaving instances of the webdriver open
    bot.stop_browser()

    # Uncomment to mark this task as finished on BotMaestro
    maestro.finish_task(
        task_id=execution.task_id,
        status=AutomationTaskFinishStatus.SUCCESS,
        message="Task Finished OK."
    )


def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
