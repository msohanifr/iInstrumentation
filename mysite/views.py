import time
import json
import pickle
from datetime import date, datetime, timedelta

import pyodbc as pyodbc
from django.http import JsonResponse, HttpResponse
from path import Path
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

from iInstrumentation.settings import MSSQL_SERVER, MSSQL_DATABASE, MSSQL_USERNAME, MSSQL_PASSWORD
from mysite.models import Profile


def test(request):
    return render(request,'test.html',{})


# ---------------------------------------------------------------
# ---------------------- MISC -----------------------------------
# ---------------------------------------------------------------

class QueryCursorByName:
    """
    This class accepts Query.Cursor and returns a tuple of {ColumnName : RowValue} for each row
    """

    def __init__(self, cursor):
        self._cursor = cursor

    def __iter__(self):
        return self

    def __next__(self):
        row = self._cursor.__next__()
        return {description[0]: row[col] for col, description in enumerate(self._cursor.description)}


def reformat_date(mydate):
    [m, d, y] = mydate.split('/')
    return y + '-' + m + '-' + d


def handler404(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)


def handler403(request):
    return render(request, '403.html', status=403)


def base(request):
    """
    This is will return all data required for BASE.HTML which will be used in all pages
    :param request:
    :return:
    """

    return {

    }


# deletes .pickle files older than one day
def delete_files():
    """
    :return:
    """
    d = Path("mysite/..")
    for i in d.listdir():
        if i.endswith(".pickle"):
            days = 60  # RETENTION PERIOD
            time_in_secs = time.time() - (days * 24 * 60 * 60)
            if i.isfile():
                if i.mtime <= time_in_secs:
                    i.remove()


# ---------------------------------------------------------------
# ---------------------- CUSTOMER -------------------------------
# ---------------------------------------------------------------


def is_user_fully_registered(user):
    """
    Tests if user has fully entered all required information and filled his profile.
    :param
    user: username from request .user
    :return:
    boolean with Profile.profile_filled
    """
    profile = Profile.objects.get(user__username=user)
    return profile.profile_filled


# --------------------------------- END_USER_PASSES_TEST -------

# QUERY DATABASE
def my_query():
    server = MSSQL_SERVER
    database = MSSQL_DATABASE
    username = MSSQL_USERNAME
    password = MSSQL_PASSWORD
    print(server, database)
    cnxn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = cnxn.cursor()
    return [cursor, cnxn]


def list_query(pk, cursor):
    result = cursor.execute(
        "SELECT SiteName, DeviceName, DeviceKey, PIDSheetNumber, DeviceDescription, UnitName "
        "FROM tblDevice JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
        "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
        "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
        "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
        "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey" +
        " WHERE DeviceKey=" + pk + ";")
    return result


# ------------------------------------------------------------------------------------------
@login_required
# @user_passes_test(is_user_email_verified, login_url='/resendemailconfirmation/')  # This should be a page that asks
# @user_passes_test(is_user_phone_verified, login_url='/sms/')
def home(request):
    print('in home')
    if request.method == 'POST':
        try:
            print('in post 1: ', request.POST)
            if request.POST['choice'] == 'true':
                with open(request.session.session_key + '.pickle', 'wb') as f:
                    pickle.dump(request.POST, f)
            print('in 1')
        except:
            print('in 2')
            # This means this POST request is not instrumentation choice request
            query_condition = "1=1"
            if request.POST['devicetag'] != "":
                devicetag = request.POST['devicetag']
                query_condition = query_condition + " AND DeviceName LIKE " + "'" + devicetag + "'"
            if request.POST['pid'] != "":
                pid = request.POST['pid']
                query_condition = query_condition + " AND PIDSheetNumber LIKE " + "'" + pid + "'"
            if request.POST['site'] != "":
                site = request.POST['site']
                query_condition = query_condition + " AND SiteName LIKE " + "'" + site + "'"
            if request.POST['unit'] != "":
                unit = request.POST['unit']
                query_condition = query_condition + " AND UnitName LIKE " + "'" + unit + "'"
            [cursor, cnxn] = my_query()
            # Sample select query
            result = cursor.execute(
                "SELECT SiteName, DeviceName, DeviceKey, PIDSheetNumber, DeviceDescription, UnitName "
                "FROM tblDevice JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
                "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
                "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
                "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
                "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey" +
                " WHERE " + query_condition + ";")
            # cursor.execute("SELECT @@version;")
            # response = base(request)
            print('in 3')
            response = {}
            for row in QueryCursorByName(cursor):
                response.update({
                    row['DeviceName']: row,
                })
            cnxn.close()
            print(response)
            return render(request, 'home.html', {'query': response})
    # request.method == GET
    try:
        print('in 4')
        [cursor, cnxn] = my_query()
        with open(request.session.session_key + '.pickle', 'rb') as f:
            data = pickle.load(f)
        chosen_vals = {}
        print(data)
        print('in 5')
        for y in data:
            print('in 6')
            try:
                print('in 7')
                result = list_query(y, cursor)
                for row in QueryCursorByName(cursor):
                    chosen_vals.update({
                        row['DeviceName']: row,
                    })
            except:
                pass
        cnxn.close()
        print('in 8')
        return render(request, 'home.html', {'query': chosen_vals})
    except:
        print('in 9')
        pass
    print('in 10')
    return render(request, 'home.html', {'query': None})


def loopcheck(request):
    """
    The results from search has to be saved inls
    :param request:
    :return:
    """
    if request.method == "POST":
        try:
            query_condition = "1=1"
            if request.POST['devicetag'] != "":
                devicetag = request.POST['devicetag']
                query_condition = query_condition + " AND DeviceName LIKE " + "'" + devicetag + "'"
            if request.POST['pid'] != "":
                pid = request.POST['pid']
                query_condition = query_condition + " AND PIDSheetNumber LIKE " + "'" + pid + "'"
            if request.POST['site'] != "":
                site = request.POST['site']
                query_condition = query_condition + " AND SiteName LIKE " + "'" + site + "'"
            if request.POST['unit'] != "":
                unit = request.POST['unit']
                query_condition = query_condition + " AND UnitName LIKE " + "'" + unit + "'"
            [cursor, cnxn] = my_query()
            # Sample select query
            cursor.execute(
                "SELECT SiteName, DeviceName, DeviceKey, PIDSheetNumber, DeviceDescription, UnitName "
                "FROM tblDevice JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
                "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
                "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
                "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
                "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey" +
                " WHERE " + query_condition + ";")

            # cursor.execute("SELECT @@version;")
            # response = base(request)
            response = {}
            for row in QueryCursorByName(cursor):
                response.update({
                    row['DeviceName']: row,
                })
            cnxn.close()
            return render(request, 'loopcheck.html', {'query': response})
        except:
            return render(request, 'loopcheck.html')
    else:  # request GET
        return render(request, 'loopcheck.html', {'query': None})


def find_id_based_on_tag(request, tag):
    """
    This function takes point TAG as parameter and finds DeviceKey and redirects page to the instrument_detail with
    instrument DeviceKey
    :param request:
    :param tag: point TAG
    :return: redirect with point ID (DeviceKey) instead of TAG so that instrument_detail can browse the tag
    """
    [cursor, cnxn] = my_query()
    cursor.execute(
        "SELECT DeviceKey FROM tblDevice "
        " WHERE DeviceName = '" + tag + "';"
    )
    for row in QueryCursorByName(cursor):
        onerow = row
    pk = onerow['DeviceKey']
    cnxn.close()
    return redirect('/iInstrumentation/instrument_detail/' + str(pk))


def instrument_detail(request, pk):
    """
    This function creates instrument detail page
    :param request:
    :param pk: Instrument DeviceKey
    :return: Instrument Detail Page
    """
    # this is for when user clicks on a tag with [TAG], at this point we have to remove the '[' and ']' and then pass
    # it to the proper function
    # use this line :::   result = cursor.execute("INSERT INTO tbltext (text) VALUES ('"+ json.dumps(test1) +"');")
    try:
        if pk[0] == '[' and pk[-1] == ']':
            tag = pk
            return redirect('/iInstrumentation/find_id_based_on_tag/' + str(tag)[1:-1])
    except:
        pass
    # -----------------------------------------------------------------------------------------------------------------
    # ----------------------------------  Browse the main information from tblDevice ----------------------------------
    #
    # :param onerow: basic information about Device
    #
    response = {}
    onerow = {}
    # Instrument general information
    # -----------------------------------------------------------------------------------------------------------------
    [cursor, cnxn] = my_query()
    try:
        cursor.execute(
            "SELECT SiteName, DeviceName, DeviceKey, DeviceLastUpdatedDateTime, DeviceLastReviewDate, "
            "DeviceTypeDescription, DeviceTypeInterlockableFlag, "
            "PIDSheetNumber, DeviceDescription, UnitName "
            "FROM tblDevice "
            "JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
            "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
            "JOIN tlkpDeviceType ON tblDevice.DeviceTypeKey = tlkpDeviceType.DeviceTypeKey "
            "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
            "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
            "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey "
            " WHERE LANXESS_UAT.dbo.tblDevice.DeviceKey=" + str(pk) + ";")
        # should get onerow from the tag itself
        for row in QueryCursorByName(cursor):
            onerow = row
    except:  # means instrument information doesn't exist in the database
        cnxn.close()
        return render(request, 'Instrument_detail.html')



    # Interlock table --------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    if onerow['DeviceTypeInterlockableFlag']:
        # Means Device is interlockable, device has interlocks
        # ----------------------------------------------------
        cursor.execute(
            " SELECT  DeviceName, dbo.tblDevice.DeviceKey, DeviceDescription, "
            " DeviceTypeDescription, DeviceLastUpdatedDateTime, DeviceCreateTS, "
            " EquipmentCode, EquipmentDescription, "
            " EquipmentActiveFlag, EquipmentCreateTS,  AreaKey, SiteUnitCreateTS, "
            " SiteName, SiteActiveFlag, SiteCreateTS, "
            " DeviceTypeDescription, UnitCode, UnitName, UnitActiveFlag, UnitCreateTS, "
            " PIDSheetNumber, PIDSheetActiveFlag, PIDSheetCreateTS,  "
            " InterlockConditionKey,  InterlockTechnologyKey, InterlockCategoryName,  InterlockConditionDescription, "
            " InterlockConditionReason, ControlSystemKey_InterlockedBy, ManualBypassKey, "
            " InterlockConditionValidationIntervalDays, InterlockConditionConsequences, InterlockConditionConcernsDate,"
            " InterlockConditionConcernsLastReviewDate, InterlockConditionConcernsHighPriorityFlag,"
            " InterlockConditionConcernsDescription,  InterlockConditionLastReviewDate,"
            " InterlockConditionLastReviewComments, InterlockConditionLastUpdatedDateTime,  "
            " InterlockConditionCreateTS,  InterlockSafetyLevelSeq, InterlockSafetyLevelDescription, "
            " InterlockSafetyLevelDefaultFlag, InterlockSafetyLevelActiveFlag "
            " FROM LANXESS_UAT.dbo.tblDevice "
            " JOIN tlkpDeviceType ON tblDevice.DeviceTypeKey = tlkpDeviceType.DeviceTypeKey"
            " JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
            " JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
            " JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
            " JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
            " JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey "
            " JOIN tblInterlockCondition ON tblDevice.DeviceKey = tblInterlockCondition.DeviceKey "
            " JOIN tlkpInterlockSafetyLevel ON tlkpInterlockSafetyLevel.InterlockSafetyLevelKey = "
            " tblInterlockCondition.InterlockSafetyLevelKey "
            " JOIN tlkpInterlockCategory ON tblInterlockCondition.InterlockCategoryKey = "
            " tlkpInterlockCategory.InterlockCategoryKey"
            " WHERE LANXESS_UAT.dbo.tblDevice.DeviceKey=" + str(pk) + ";")
    else:
        tag = onerow['DeviceName']
        cursor.execute(
            "SELECT DeviceName, tD.DeviceKey, * FROM tblInterlockCondition "
            " JOIN tblDevice tD on tblInterlockCondition.DeviceKey = tD.DeviceKey "
            " JOIN tlkpInterlockSafetyLevel ON tlkpInterlockSafetyLevel.InterlockSafetyLevelKey = "
            " tblInterlockCondition.InterlockSafetyLevelKey " 
            " JOIN tlkpInterlockCategory ON tblInterlockCondition.InterlockCategoryKey = "
            " tlkpInterlockCategory.InterlockCategoryKey "
            " WHERE tblInterlockCondition.InterlockConditionDescription like '%" + tag + "]%'; "
        )
    for row in QueryCursorByName(cursor):
        response.update({
            row['InterlockConditionKey']: row
        })

    cursor.execute(
        " SELECT * FROM tblControlValveModulating "
        " WHERE LANXESS_UAT.dbo.tblControlValveModulating.DeviceKey=" + str(pk) + ";")
    # should get onerow from the tag itself
    for row in QueryCursorByName(cursor):
        print(row)
        onerow[row['ValveKey']] = row
    print("this is the 1: ", onerow)
    cnxn.close()
    return render(request, 'instrument_templates_spec/ControlValve.html', {'response': response, 'onerow': onerow})
    return render(request, 'Instrument_detail.html', {'response': response, 'onerow': onerow})


def prooftest(request, pk):
    response = {}
    onerow = ''
    [cursor, cnxn] = my_query()
    # The Device information. on the top of the page
    cursor.execute(
        "SELECT SiteName, DeviceName, DeviceKey, DeviceLastUpdatedDateTime, "
        "DeviceLastReviewDate, DeviceTypeDescription, tblDevice.DeviceTypeKey, DeviceTypeInterlockableFlag, "
        "PIDSheetNumber, DeviceDescription, UnitName "
        "FROM tblDevice JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
        "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
        "JOIN tlkpDeviceType ON tblDevice.DeviceTypeKey = tlkpDeviceType.DeviceTypeKey "
        "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
        "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
        "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey " +
        " WHERE LANXESS_UAT.dbo.tblDevice.DeviceKey=" + str(pk) + ";")
    # should get onerow from the tag itself
    for row in QueryCursorByName(cursor):
        onerow = row
    '''
      if (onerow['DeviceTypeInterlockableFlag']):
        cursor.execute(
            " SELECT DeviceName, dbo.tblDevice.DeviceKey, DeviceDescription, LANXESS_UAT.dbo.tblDevice.DeviceTypeKey , "
            " DeviceTypeDescription, DeviceLastUpdatedDateTime, DeviceCreateTS, "
            " EquipmentCode, EquipmentDescription, "
            " EquipmentActiveFlag, EquipmentCreateTS,  AreaKey, SiteUnitCreateTS, SiteName, SiteActiveFlag, SiteCreateTS, "
            " DeviceTypeDescription, UnitCode, UnitName, UnitActiveFlag, UnitCreateTS, "
            " PIDSheetNumber, PIDSheetActiveFlag, PIDSheetCreateTS,  "
            " InterlockConditionKey,  InterlockTechnologyKey, InterlockCategoryName,  InterlockConditionDescription, "
            " InterlockConditionReason, ControlSystemKey_InterlockedBy, ManualBypassKey, "
            " InterlockConditionValidationIntervalDays, InterlockConditionConsequences, InterlockConditionConcernsDate,"
            " InterlockConditionConcernsLastReviewDate, InterlockConditionConcernsHighPriorityFlag,"
            " InterlockConditionConcernsDescription,  InterlockConditionLastReviewDate,"
            " InterlockConditionLastReviewComments, InterlockConditionLastUpdatedDateTime,  "
            " InterlockConditionCreateTS,  InterlockSafetyLevelSeq, InterlockSafetyLevelDescription, "
            " InterlockSafetyLevelDefaultFlag, InterlockSafetyLevelActiveFlag "
            " FROM LANXESS_UAT.dbo.tblDevice"
            " JOIN tlkpDeviceType ON tblDevice.DeviceTypeKey = tlkpDeviceType.DeviceTypeKey"
            " JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
            " JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
            " JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
            " JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
            " JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey "
            " JOIN tblInterlockCondition ON tblDevice.DeviceKey = tblInterlockCondition.DeviceKey "
            " JOIN tlkpInterlockSafetyLevel ON tlkpInterlockSafetyLevel.InterlockSafetyLevelKey = "
            " tblInterlockCondition.InterlockSafetyLevelKey "
            " JOIN tlkpInterlockCategory ON tblInterlockCondition.InterlockCategoryKey = "
            " tlkpInterlockCategory.InterlockCategoryKey"
            " WHERE LANXESS_UAT.dbo.tblDevice.DeviceKey=" + str(pk) + ";")
    else:
        tag = onerow['DeviceName']
        cursor.execute(
            "SELECT DeviceName, tD.DeviceKey, DeviceTypeKey, * FROM tblInterlockCondition "
            " JOIN tblDevice tD on tblInterlockCondition.DeviceKey = tD.DeviceKey "
            " JOIN tlkpInterlockSafetyLevel ON tlkpInterlockSafetyLevel.InterlockSafetyLevelKey = "
            " tblInterlockCondition.InterlockSafetyLevelKey "
            " JOIN tlkpInterlockCategory ON tblInterlockCondition.InterlockCategoryKey = "
            " tlkpInterlockCategory.InterlockCategoryKey"
            " WHERE tblInterlockCondition.InterlockConditionDescription like '%" + tag + "%'; "
        )
    '''

    for row in QueryCursorByName(cursor):
        response.update({
            row['InterlockConditionKey']: row
        })

    cursor.execute(
        "SELECT HtmlPageAddress from tblHtmlTemplateProoftest"
        " JOIN tblDevicePageProoftest tHPT on tHPT.HtmlKey = tblHtmlTemplateProoftest.HtmlKey "
        " JOIN tblDevice tDP on tHPT.DeviceTypeKey = tDP.DeviceTypeKey"
        " WHERE tDP.DeviceTypeKey='" + str(onerow['DeviceTypeKey']) + "';"
    )
    htmlpage = {
        'HtmlPageAddress': 'NotDefined.html'
    }
    for i in QueryCursorByName(cursor):
        htmlpage = i
    cnxn.close()
    print(htmlpage['HtmlPageAddress'])
    return render(request, 'instrument_templates_prooftest/' + htmlpage['HtmlPageAddress'],
                  {'response': response, 'onerow': onerow})


def logout(request):
    return redirect('/accounts/logout/')


# ajax functions for looking up the text in INPUT
def devicetagajax(request):
    query_condition = "1=1"
    devicetag = request.GET['devicetag']
    query_condition = query_condition + " AND DeviceName LIKE" + "'%" + devicetag + "%'"
    # we need to query database for the tag
    [cursor, cnxn] = my_query()
    # Sample select query
    result = cursor.execute(
        "SELECT DISTINCT TOP 10 DeviceName FROM tblDevice "
        "JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
        "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
        "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
        "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
        "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey" +
        " WHERE " + query_condition +
        " ORDER BY DeviceName;")
    # cursor.execute("SELECT @@version;")
    q_result = []
    for i in result.fetchall():
        q_result.append(i[0])
    cnxn.close()
    return JsonResponse({
        'data': q_result
    })


def pidajax(request):
    query_condition = "1=1"
    pid = request.GET['pid']
    query_condition = query_condition + " AND PIDSheetNumber LIKE" + "'%" + pid + "%'"
    # we need to query database for the tag
    [cursor, cnxn] = my_query()
    # Sample select query
    result = cursor.execute(
        "SELECT DISTINCT TOP 10 PIDSheetNumber FROM tblDevice "
        "JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
        "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
        "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
        "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
        "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey" +
        " WHERE " + query_condition +
        " ORDER BY PIDSheetNumber;")
    # cursor.execute("SELECT @@version;")
    q_result = []
    for i in result.fetchall():
        q_result.append(i[0])
    cnxn.close()
    return JsonResponse({
        'data': q_result
    })


def siteajax(request):
    query_condition = "1=1"
    site = request.GET['site']
    query_condition = query_condition + " AND SiteName LIKE" + "'%" + site + "%'"
    # we need to query database for the tag
    [cursor, cnxn] = my_query()
    # Sample select query
    result = cursor.execute(
        "SELECT DISTINCT TOP 10 SiteName FROM tblDevice "
        "JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
        "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
        "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
        "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
        "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey" +
        " WHERE " + query_condition +
        " ORDER BY SiteName;")
    # cursor.execute("SELECT @@version;")
    q_result = []
    for i in result.fetchall():
        q_result.append(i[0])
    cnxn.close()
    return JsonResponse({
        'data': q_result
    })


def unitajax(request):
    query_condition = "1=1"
    unit = request.GET['unit']
    query_condition = query_condition + " AND UnitName LIKE" + "'%" + unit + "%'"
    # we need to query database for the tag
    [cursor, cnxn] = my_query()
    # Sample select query
    result = cursor.execute(
        "SELECT DISTINCT TOP 10 UnitName FROM tblDevice "
        "JOIN tlkpEquipment tE on tblDevice.EquipmentKey = tE.EquipmentKey "
        "JOIN tblSiteUnit tSU on tE.SiteUnitKey = tSU.SiteUnitKey "
        "JOIN tblSite tS on tSU.SiteKey = tS.SiteKey "
        "JOIN tlkpUnit ON tSU.UnitKey = tlkpUnit.UnitKey "
        "JOIN tlkpPIDSheet ON dbo.tblDevice.PIDSheetKey=dbo.tlkpPIDSheet.PIDSheetKey" +
        " WHERE " + query_condition +
        " ORDER BY UnitName;")
    # cursor.execute("SELECT @@version;")
    q_result = []
    for i in result.fetchall():
        q_result.append(i[0])
    cnxn.close()
    return JsonResponse({
        'data': q_result
    })


# settings
def devicetypehtmlProoftest(request):
    [cursor, cnxn] = my_query()
    print(request.POST)
    print('1')
    if request.method == 'POST':
        for i in request.POST:
            print('This is: ', i)
            if request.POST[i] == 'N/A':
                cursor.execute(
                    "DELETE FROM LANXESS_UAT.dbo.tblDevicePageProoftest "
                    " WHERE DeviceTypeKey='" + i + "';"
                )
                cnxn.commit()
                continue;
            print('in the middle')
            try:
                cursor.execute(
                    "UPDATE LANXESS_UAT.dbo.tblDevicePageProoftest "
                    " SET HtmlKey = " + request.POST[i] + " WHERE DeviceTypeKey='" + i + "'"
                                                                                         " IF @@ROWCOUNT = 0 "
                                                                                         " INSERT INTO LANXESS_UAT.dbo.tblDevicePageProoftest(DeviceTypeKey,HtmlKey) VALUES ('" + i + "','" +
                    request.POST[i] + "');"
                )
                cnxn.commit()
            except:
                pass

    cnxn.close()
    print('2')
    [cursor, cnxn] = my_query()
    print('3')
    result = cursor.execute(
        " SELECT DeviceTypeKey as 'DeviceTypeKey', "
        "       DeviceTypeCode as 'DeviceTypeCode', "
        "       DeviceTypeDescription as 'DeviceTypeDescription'"
        " FROM tlkpDeviceType;"
    )
    print('4')
    DeviceType = result.fetchall()
    cnxn.close()
    print('5')
    [cursor, cnxn] = my_query()
    result = cursor.execute(
        " SELECT id, DeviceTypeKey, HtmlKey "
        " FROM tblDevicePageProoftest;"
    )
    print('6')
    DevicePage = result.fetchall()
    cnxn.close()
    print('7')
    [cursor, cnxn] = my_query()
    result = cursor.execute(
        " SELECT * FROM tblHtmlTemplateProoftest;"
    )
    DeviceHTML = result.fetchall()
    cnxn.close()
    return render(request, 'settings/DeviceTypeTemplate.html', {
        'DeviceType': DeviceType,
        'DevicePage': DevicePage,
        'DeviceHTML': DeviceHTML,
    })
