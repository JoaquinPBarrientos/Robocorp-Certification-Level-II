from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_the_intranet_website()
    log_in()
    get_in_Order_Your_Robot()
    orders = get_orders()
    order_robot(orders)
    archive_receipts()

    


def open_the_intranet_website():
    """Navigates to the given URL"""
    browser.goto("https://robotsparebinindustries.com/")

def log_in():
    """Fills in the login form and clicks the 'Log in' button"""   
    page = browser.page()
    page.fill("#username", "maria")
    page.fill("#password", "thoushallnotpass")
    page.click("button:text('Log in')") #page.click("button[type=submit]") 

def get_orders():
    """ Downloads the CSV file with the data to order robots. """
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv",overwrite=True)

    tables = Tables()
    table = tables.read_table_from_csv("orders.csv")

    return table

def get_in_Order_Your_Robot():
    """Selects the 'Order Your Robot' section"""
    page = browser.page()
    page.click("a:text('Order Your Robot')")

def close_annoying_modal():
    """Closes the annoying modal"""
    page = browser.page()
    page.click("button:text('OK')")
    
def order_robot(data: Tables):
    """ Orders robots from RobotSpareBin Industries Inc. """
    page = browser.page()
    for row in data:
        
        close_annoying_modal()
        page.select_option("#head", row["Head"])
        page.check(f"#id-body-{row['Body']}")
        page.fill("input[placeholder='Enter the part number for the legs']", row["Legs"])
        page.fill("#address", str(row["Address"]))
        page.click("button:text('Preview')")
        page.click("button:text('Order')")

        while not page.query_selector("#order-another"):
            page.click("#order")

        pdf_creation(row["Order number"])
        
        page.click("button:text('Order another robot')")
        


def store_receipt_as_pdf(order_number: int):
    """ Saves the order HTML receipt as a PDF file. """
    page = browser.page()
    sales_receipt_html = page.locator("#receipt").inner_html()
    pdf = PDF()
    pdf_file = f"output/sale_receipt_order_{order_number}.pdf"
    pdf.html_to_pdf(sales_receipt_html,pdf_file)
    
    return pdf_file

def screenshot_robot(order_number: int):
    """ Saves the screenshot of the ordered robot. """
    page = browser.page()
    page = page.query_selector("#robot-preview-image")
    screenshot_file = f"output/robot_order_{order_number}.png"
    page.screenshot(path=screenshot_file)

    return screenshot_file


def embed_screenshot_to_receipt(screenshot_file: str, pdf_file: str):
    """ Embeds the screenshot of the robot to the PDF receipt. """
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot_file], target_document=pdf_file, append=True)

def pdf_creation(order_number: int):
    """ Creates ZIP archive of the receipts and the images. """
    pdf_file = store_receipt_as_pdf(order_number)
    screenshot_file = screenshot_robot(order_number)
    embed_screenshot_to_receipt(screenshot_file, pdf_file)


def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output", "output/output.zip",include = "*.pdf")
                
