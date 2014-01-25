
Module mFDS2Render
    Dim dset As New Dataset1
    Dim DataTableAppearances As DataTable
    Dim ObstructionAppearanceIndex() As Integer
    Dim VentAppearanceIndex() As Integer

    Public COuntVentsWithXB As Integer
    Public dlgStatus As New fStatus
    Public FDSLineCOunt As Integer
    Sub Main()
        Dim FileNum As Integer = FreeFile()
        Dim FileNameFDS As String
        Dim FileNameGE1 As String
        Dim i, j As Integer

        Dim dlg As New OpenFileDialog


        DataTableAppearances = dset.Tables("Appearances")

        dlg.Title = "Select FDS Input File"
        dlg.Filter = "FDS Data Files (*.fds)|*.fds|All Files (*.*)|*.*"
        If dlg.ShowDialog <> DialogResult.OK Then End
        dlgStatus.Show()
        dlgStatus.lstStatus.Items.Add("Reading FDS File") : Application.DoEvents()
        FileNameFDS = dlg.FileName
        ReadNameListFile(FileNameFDS)
        If IsNothing(Obstructions) Then End

        dlgStatus.lstStatus.Items.Add("Reading Surface Appearances") : Application.DoEvents()
        AddAppearancesToDataTable()

        dlgStatus.lstStatus.Items.Add("Match Obstructions to Appearances") : Application.DoEvents()
        MatchObstructionsToAppearances()

        dlgStatus.lstStatus.Items.Add("Match Vents to Appearances") : Application.DoEvents()
        MatchVentsToAppearances()

        i = FileNameFDS.LastIndexOf(".")
        FileNameGE1 = FileNameFDS.Substring(0, i) & ".ge1"

        FileOpen(FileNum, FileNameGE1, OpenMode.Output, OpenAccess.Default, OpenShare.Default)


        dlgStatus.lstStatus.Items.Add("Writing Appearances") : Application.DoEvents()
        PutAppearancesInFile(FileNum)
        dlgStatus.lstStatus.Items.Add("Writing Obstructions") : Application.DoEvents()
        PutObstructionsVentsInFile(FileNum)
        FileClose(FileNum)


        dlgStatus.lstStatus.Items.Add("Adding Render File to FDS File") : Application.DoEvents()
        AddCADGEOMToFDSFile(FileNameFDS, FileNameGE1)
        End

    End Sub
    Sub MatchObstructionsToAppearances()
        ReDim ObstructionAppearanceIndex(Obstructions.GetUpperBound(0) * 7)
        Dim dv As DataView = New DataView(DataTableAppearances)
        Dim ObstructionFaceIndex As Integer
        Dim TopAppearance As Integer
        Dim BottomAppearance As Integer
        Dim LeftAppearance As Integer
        Dim RightAppearance As Integer
        Dim FrontAppearance As Integer
        Dim BackAppearance As Integer
        Dim MaxApperanceIndex As Integer
        Dim Appearance As Integer
        Dim i, j As Integer

        Dim RGB() As String
        Dim R, G, B As Integer
        Dim ID As String
        Dim VariableNames(), VariableValues() As String
        Dim ColorText As String
        Dim SURFID, SURFIDS() As String
        dv.RowFilter = "AppearanceIndex IS NOT NULL"
        dv.Sort = "AppearanceIndex"

        MaxApperanceIndex = dv(dv.Count - 1).Item("AppearanceIndex")
        ObstructionFaceIndex = 0
        dlgStatus.ProgressBar1.Maximum = Obstructions.GetUpperBound(0)
        For i = 0 To Obstructions.GetUpperBound(0)
            dlgStatus.ProgressBar1.Value = i
            FrontAppearance = 0
            BackAppearance = 0
            LeftAppearance = 0
            RightAppearance = 0
            BottomAppearance = 0
            TopAppearance = 0



            ParseNameList(ObstructionProperties(i).ToUpper, ID, ID, VariableNames, VariableValues)

            '            AppearanceIndex += 1
            If ObstructionProperties(i).IndexOf("COLOR") >= 0 Or ObstructionProperties(i).IndexOf("RGB") >= 0 Then
                For j = 0 To VariableNames.GetUpperBound(0)
                    If VariableNames(j) = "COLOR" Then
                        ColorText = VariableValues(j)
                        ColorText = ColorText.Replace("'", "")
                        dv.RowFilter = "Description='" & ColorText & "'"
                        If dv.Count > 0 Then
                            If dv(0).Item("AppearanceIndex") Is DBNull.Value Then
                                MaxApperanceIndex += 1
                                dv(0).Item("AppearanceIndex") = MaxApperanceIndex
                            End If
                            Appearance = dv(0).Item("AppearanceIndex")

                            FrontAppearance = Appearance
                            BackAppearance = Appearance
                            LeftAppearance = Appearance
                            RightAppearance = Appearance
                            BottomAppearance = Appearance
                            TopAppearance = Appearance
                        End If
                    ElseIf VariableNames(j) = "RGB" Then
                        ColorText = VariableValues(j)
                        ColorText = ColorText.Replace("'", "")
                        RGB = ColorText.Split(",")
                        ID = "RGB" & ColorText.Replace(",", "").Replace(" ", "")

                        dv.RowFilter = "Description='" & ID & "'"
                        If dv.Count > 0 Then
                            'Found the appearance
                            If dv(0).Item("AppearanceIndex") Is DBNull.Value Then
                                MaxApperanceIndex += 1
                                dv(0).Item("AppearanceIndex") = MaxApperanceIndex
                            End If
                            Appearance = dv(0).Item("AppearanceIndex")
                        Else
                            'Did not find RGB in datatable put a new one in
                            MaxApperanceIndex += 1
                            Appearance = MaxApperanceIndex
                            R = -1
                            G = -1
                            B = -1
                            If RGB.GetUpperBound(0) = 2 Then
                                R = Val(RGB(0))
                                G = Val(RGB(1))
                                B = Val(RGB(2))
                            End If
                            AddAppearanceToDataTable(ID, R, G, B, MaxApperanceIndex)
                        End If


                        FrontAppearance = Appearance
                        BackAppearance = Appearance
                        LeftAppearance = Appearance
                        RightAppearance = Appearance
                        BottomAppearance = Appearance
                        TopAppearance = Appearance



                    End If
                Next
            ElseIf ObstructionProperties(i).IndexOf("SURF_ID6") >= 0 Then
                GetFaceAppearanceIndexFromSURF_IDVariables(VariableNames, VariableValues, MaxApperanceIndex, dv, FrontAppearance, BackAppearance, LeftAppearance, RightAppearance, BottomAppearance, TopAppearance)
            ElseIf ObstructionProperties(i).IndexOf("SURF_IDS") >= 0 Then
                GetFaceAppearanceIndexFromSURF_IDVariables(VariableNames, VariableValues, MaxApperanceIndex, dv, FrontAppearance, BackAppearance, LeftAppearance, RightAppearance, BottomAppearance, TopAppearance)

            ElseIf ObstructionProperties(i).IndexOf("SURF_ID") >= 0 Then
                GetFaceAppearanceIndexFromSURF_IDVariables(VariableNames, VariableValues, MaxApperanceIndex, dv, FrontAppearance, BackAppearance, LeftAppearance, RightAppearance, BottomAppearance, TopAppearance)
            End If

            ObstructionAppearanceIndex(ObstructionFaceIndex) = FrontAppearance
            ObstructionAppearanceIndex(ObstructionFaceIndex + 1) = BackAppearance
            ObstructionAppearanceIndex(ObstructionFaceIndex + 2) = LeftAppearance
            ObstructionAppearanceIndex(ObstructionFaceIndex + 3) = RightAppearance
            ObstructionAppearanceIndex(ObstructionFaceIndex + 4) = BottomAppearance
            ObstructionAppearanceIndex(ObstructionFaceIndex + 5) = TopAppearance
            ObstructionFaceIndex += 6
        Next



    End Sub



    Sub MatchVentsToAppearances()
        ReDim VentAppearanceIndex(Vents.GetUpperBound(0))
        Dim dv As DataView = New DataView(DataTableAppearances)
        Dim VentIndex As Integer
        Dim Appearance As Integer
        Dim i, j As Integer
        Dim MaxApperanceIndex As Integer
        Dim RGB() As String
        Dim R, G, B As Integer
        Dim ID As String
        Dim VariableNames(), VariableValues() As String
        Dim ColorText As String
        Dim SURFID, SURFIDS() As String
        dv.RowFilter = "AppearanceIndex IS NOT NULL"
        dv.Sort = "AppearanceIndex"

        MaxApperanceIndex = dv(dv.Count - 1).Item("AppearanceIndex")        
        dlgStatus.ProgressBar1.Maximum = Vents.GetUpperBound(0)
        For i = 0 To Vents.GetUpperBound(0)
            dlgStatus.ProgressBar1.Value = i
            Appearance = 0

            ParseNameList(VentProperties(i).ToUpper, ID, ID, VariableNames, VariableValues)
            If VentProperties(i).IndexOf("COLOR") >= 0 Or VentProperties(i).IndexOf("RGB") >= 0 Then
                For j = 0 To VariableNames.GetUpperBound(0)
                    If VariableNames(j) = "COLOR" Then
                        ColorText = VariableValues(j)
                        ColorText = ColorText.Replace("'", "")
                        dv.RowFilter = "Description='" & ColorText & "'"
                        If dv.Count > 0 Then
                            If dv(0).Item("AppearanceIndex") Is DBNull.Value Then
                                MaxApperanceIndex += 1
                                dv(0).Item("AppearanceIndex") = MaxApperanceIndex
                            End If
                            Appearance = dv(0).Item("AppearanceIndex")

                        End If
                    ElseIf VariableNames(j) = "RGB" Then
                        ColorText = VariableValues(j)
                        ColorText = ColorText.Replace("'", "")
                        RGB = ColorText.Split(",")
                        ID = "RGB" & ColorText.Replace(",", "").Replace(" ", "")

                        dv.RowFilter = "Description='" & ID & "'"
                        If dv.Count > 0 Then
                            'Found the appearance
                            If dv(0).Item("AppearanceIndex") Is DBNull.Value Then
                                MaxApperanceIndex += 1
                                dv(0).Item("AppearanceIndex") = MaxApperanceIndex
                            End If
                            Appearance = dv(0).Item("AppearanceIndex")
                        Else
                            'Did not find RGB in datatable put a new one in
                            MaxApperanceIndex += 1
                            Appearance = MaxApperanceIndex
                            R = -1
                            G = -1
                            B = -1
                            If RGB.GetUpperBound(0) = 2 Then
                                R = Val(RGB(0))
                                G = Val(RGB(1))
                                B = Val(RGB(2))
                            End If
                            AddAppearanceToDataTable(ID, R, G, B, MaxApperanceIndex)
                        End If





                    End If
                Next
            ElseIf VentProperties(i).IndexOf("SURF_ID") >= 0 Then
                GetFaceAppearanceIndexFromSURF_IDVariables(VariableNames, VariableValues, MaxApperanceIndex, dv, Appearance)
            End If

            VentAppearanceIndex(i) = Appearance
        Next



    End Sub



    Sub AddAppearancesToDataTable()
        Dim AppearanceIndex As Integer
        Dim dv As DataView = New DataView(DataTableAppearances)
        Dim ColorText As String
        Dim R, G, B As Integer
        Dim RGB() As String
        AddAppearanceToDataTable("RANDOM", -1, -1, -1, 0)
        AddAppearanceToDataTable("INERT", 238, 216, 174, 1)
        AddAppearanceToDataTable("OPEN", 1, 1, 1, 2)
        AppearanceIndex = 2
        AddAllFDSColorToAppearanceDataTable()


        Dim i, j As Integer
        Dim NameListType, ID As String
        Dim Variablenames(), VariableValues() As String
        'FDS SURF Variables first
        For i = 0 To Surfaces.GetUpperBound(0)
            ParseNameList(SurfaceProperties(i).ToUpper, NameListType, ID, Variablenames, VariableValues)
            ID = Surfaces(i)
            R = -1
            G = -1
            B = -1
            AppearanceIndex += 1
            If SurfaceProperties(i).IndexOf("COLOR") >= 0 Or SurfaceProperties(i).IndexOf("RGB") >= 0 Then
                For j = 0 To Variablenames.GetUpperBound(0)
                    If Variablenames(j) = "COLOR" Then
                        ColorText = VariableValues(j)
                        ColorText = ColorText.Replace("'", "")
                        dv.RowFilter = "Description='" & ColorText & "'"
                        If dv.Count > 0 Then
                            R = dv(0).Item("R")
                            G = dv(0).Item("G")
                            B = dv(0).Item("B")
                        End If
                    ElseIf Variablenames(j) = "RGB" Then
                        ColorText = VariableValues(j)
                        ColorText = ColorText.Replace("'", "")
                        RGB = ColorText.Split(",")
                        'ID = "RGB" & ColorText.Replace(",", "").Replace(" ", "")
                        If RGB.GetUpperBound(0) = 2 Then
                            R = Val(RGB(0))
                            G = Val(RGB(1))
                            B = Val(RGB(2))
                        End If
                    End If
                Next

            End If
            ' End If
            AddAppearanceToDataTable(ID, R, G, B, AppearanceIndex)
        Next


    End Sub

    Sub PutAppearancesInFile(ByVal FileNum As Integer)

        Dim dv As DataView = New DataView(DataTableAppearances)
        Dim i, j As Integer
        Dim a As String
        Dim Description As String
        dv.RowFilter = "AppearanceIndex IS NOT NULL"
        dv.Sort = "AppearanceIndex "



        PrintLine(FileNum, "[APPEARANCE]")
        PrintLine(FileNum, dv.Count)
        dlgStatus.ProgressBar1.Maximum = dv.Count - 1
        For i = 0 To dv.Count - 1
            dlgStatus.ProgressBar1.Value = i
            Description = "" & dv(i).Item("Description")
            PrintLine(FileNum, Description)
            a = i & " "
            a &= dv(i).Item("R") & " "
            a &= dv(i).Item("G") & " "
            a &= dv(i).Item("B") & " "
            If Description = "OPEN" Then a &= "1 1 0 "
            '        a &= "1 1 1 800" 'texture size, shinyness, transparancy
            PrintLine(FileNum, a)
            PrintLine(FileNum, "" & dv(i).Item("tfile"))
        Next

    End Sub

    Sub PutObstructionsVentsInFile(ByVal FileNum As Integer)

        Dim FaceCount, i, j As Integer
        Dim XB() As String
        Dim XBString As String
        Dim X0, X1, Y0, Y1, Z0, Z1 As Single
        Dim NameListType As String
        Dim ID As String
        Dim VariableNames() As String
        Dim VariableValues() As String
        Dim Front, Back, Left, Right, Bottom, Top As String
        Dim LocationString As String
        Dim FaceAppearanceIndex As Integer

        PrintLine(FileNum, "[FACES]")


        FaceCount = (Obstructions.GetUpperBound(0) + 1) * 6
        PrintLine(FileNum, FaceCount + COuntVentsWithXB)
        FaceAppearanceIndex = 0
        dlgStatus.ProgressBar1.Maximum = Obstructions.GetUpperBound(0)
        For i = 0 To Obstructions.GetUpperBound(0)
            dlgStatus.ProgressBar1.Value = i
            ParseNameList(ObstructionProperties(i), NameListType, ID, VariableNames, VariableValues)

            For j = 0 To VariableNames.GetUpperBound(0)
                If VariableNames(j) = "XB" Then
                    LocationString = VariableValues(j).Trim
                    LocationString = LocationString.Replace(" ", ",")
                    LocationString = LocationString.Replace(",,", ",")
                    XB = LocationString.Split(",")
                    If XB.GetUpperBound(0) <> 5 Then
                        ID = ""
                    Else
                        X0 = CSng(XB(0))
                        X1 = CSng(XB(1))
                        Y0 = CSng(XB(2))
                        Y1 = CSng(XB(3))
                        Z0 = CSng(XB(4))
                        Z1 = CSng(XB(5))


                        Front = X0 & " " & Y0 & " " & Z0 & " " & X1 & " " & Y0 & " " & Z0 & " " & X1 & " " & Y0 & " " & Z1 & " " & X0 & " " & Y0 & " " & Z1
                        Left = X0 & " " & Y0 & " " & Z0 & " " & X0 & " " & Y0 & " " & Z1 & " " & X0 & " " & Y1 & " " & Z1 & " " & X0 & " " & Y1 & " " & Z0
                        Right = X1 & " " & Y0 & " " & Z0 & " " & X1 & " " & Y1 & " " & Z0 & " " & X1 & " " & Y1 & " " & Z1 & " " & X1 & " " & Y0 & " " & Z1

                        Back = X0 & " " & Y1 & " " & Z0 & " " & X0 & " " & Y1 & " " & Z1 & " " & X1 & " " & Y1 & " " & Z1 & " " & X1 & " " & Y1 & " " & Z0

                        Bottom = X0 & " " & Y0 & " " & Z0 & " " & X0 & " " & Y1 & " " & Z0 & " " & X1 & " " & Y1 & " " & Z0 & " " & X1 & " " & Y0 & " " & Z0
                        Top = X0 & " " & Y0 & " " & Z1 & " " & X1 & " " & Y0 & " " & Z1 & " " & X1 & " " & Y1 & " " & Z1 & " " & X0 & " " & Y1 & " " & Z1




                        PrintLine(FileNum, Front & " " & ObstructionAppearanceIndex(FaceAppearanceIndex + 0))
                        PrintLine(FileNum, Back & " " & ObstructionAppearanceIndex(FaceAppearanceIndex + 1))

                        PrintLine(FileNum, Left & " " & ObstructionAppearanceIndex(FaceAppearanceIndex + 2))
                        PrintLine(FileNum, Right & " " & ObstructionAppearanceIndex(FaceAppearanceIndex + 3))
                        PrintLine(FileNum, Bottom & " " & ObstructionAppearanceIndex(FaceAppearanceIndex + 4))
                        PrintLine(FileNum, Top & " " & ObstructionAppearanceIndex(FaceAppearanceIndex + 5))
                        FaceAppearanceIndex += 6
                    End If
                End If
            Next
        Next
        'Put Vents in File
        If COuntVentsWithXB > 0 Then
            dlgStatus.lstStatus.Items.Add("Adding Vents to Geometry File")
            dlgStatus.ProgressBar1.Maximum = Vents.GetUpperBound(0)
            FaceAppearanceIndex = 0
            For i = 0 To Vents.GetUpperBound(0)
                dlgStatus.ProgressBar1.Value = i
                If CStr(VentProperties(VentProperties.GetUpperBound(0))).ToUpper.Replace(" ", "").IndexOf("XB=") >= 0 Then
                    ParseNameList(VentProperties(i), NameListType, ID, VariableNames, VariableValues)

                    For j = 0 To VariableNames.GetUpperBound(0)
                        If VariableNames(j) = "XB" Then
                            LocationString = VariableValues(j).Trim
                            LocationString = LocationString.Replace(" ", ",")
                            LocationString = LocationString.Replace(",,", ",")
                            XB = LocationString.Split(",")
                            If XB.GetUpperBound(0) <> 5 Then
                                ID = ""
                            Else
                                X0 = CSng(XB(0))
                                X1 = CSng(XB(1))
                                Y0 = CSng(XB(2))
                                Y1 = CSng(XB(3))
                                Z0 = CSng(XB(4))
                                Z1 = CSng(XB(5))

                                If X0 = X1 Then
                                    XBString = X0 & " " & Y0 & " " & Z0 & " " & X0 & " " & Y0 & " " & Z1 & " " & X0 & " " & Y1 & " " & Z1 & " " & X0 & " " & Y1 & " " & Z0
                                ElseIf Y0 = Y1 Then
                                    XBString = X0 & " " & Y0 & " " & Z0 & " " & X0 & " " & Y0 & " " & Z1 & " " & X1 & " " & Y0 & " " & Z1 & " " & X1 & " " & Y0 & " " & Z0
                                Else 'If Z0 = Z1 Then
                                    XBString = X0 & " " & Y0 & " " & Z0 & " " & X0 & " " & Y1 & " " & Z0 & " " & X1 & " " & Y1 & " " & Z0 & " " & X1 & " " & Y0 & " " & Z0
                                End If



                                PrintLine(FileNum, XBString & " " & VentAppearanceIndex(FaceAppearanceIndex + 0))
                                FaceAppearanceIndex += 1
                            End If
                        End If
                    Next
                End If
            Next
        End If
        '

    End Sub


    Sub AddAppearanceToDataTable(ByVal Description As String, ByVal R As Integer, ByVal G As Integer, ByVal B As Integer, Optional ByVal AppearanceIndex As Integer = -1)
        Dim dr As DataRow

        If R > 0 And R < 1 Then R = R * 255
        If G > 0 And G < 1 Then G = G * 255
        If B > 0 And B < 1 Then B = B * 255

        dr = DataTableAppearances.NewRow
        dr("Description") = Description
        dr("R") = R
        dr("G") = G
        dr("B") = B
        If AppearanceIndex > -1 Then dr("AppearanceIndex") = AppearanceIndex

        DataTableAppearances.Rows.Add(dr)


    End Sub

    Sub AddAllFDSColorToAppearanceDataTable()
        AddAppearanceToDataTable("ALICE BLUE", 240, 248, 255)
        AddAppearanceToDataTable("ANTIQUE WHITE", 250, 235, 215)
        AddAppearanceToDataTable("ANTIQUE WHITE 1", 255, 239, 219)
        AddAppearanceToDataTable("ANTIQUE WHITE 2", 238, 223, 204)
        AddAppearanceToDataTable("ANTIQUE WHITE 3", 205, 192, 176)
        AddAppearanceToDataTable("ANTIQUE WHITE 4", 139, 131, 120)
        AddAppearanceToDataTable("AQUAMARINE", 127, 255, 212)
        AddAppearanceToDataTable("AQUAMARINE 1", 118, 238, 198)
        AddAppearanceToDataTable("AQUAMARINE 2", 102, 205, 170)
        AddAppearanceToDataTable("AQUAMARINE 3", 69, 139, 116)
        AddAppearanceToDataTable("AZURE", 240, 255, 255)
        AddAppearanceToDataTable("AZURE 1", 224, 238, 238)
        AddAppearanceToDataTable("AZURE 2", 193, 205, 205)
        AddAppearanceToDataTable("AZURE 3", 131, 139, 139)
        AddAppearanceToDataTable("BANANA", 227, 207, 87)
        AddAppearanceToDataTable("BEIGE", 245, 245, 220)
        AddAppearanceToDataTable("BISQUE", 255, 228, 196)
        AddAppearanceToDataTable("BISQUE 1", 238, 213, 183)
        AddAppearanceToDataTable("BISQUE 2", 205, 183, 158)
        AddAppearanceToDataTable("BISQUE 3", 139, 125, 107)
        AddAppearanceToDataTable("BLACK", 0, 0, 0)
        AddAppearanceToDataTable("BLANCHED ALMOND", 255, 235, 205)
        AddAppearanceToDataTable("BLUE", 0, 0, 255)
        AddAppearanceToDataTable("BLUE 2", 0, 0, 238)
        AddAppearanceToDataTable("BLUE 3", 0, 0, 205)
        AddAppearanceToDataTable("BLUE 4", 0, 0, 139)
        AddAppearanceToDataTable("BLUE VIOLET", 138, 43, 226)
        AddAppearanceToDataTable("BRICK", 156, 102, 31)
        AddAppearanceToDataTable("BROWN", 255, 64, 64)
        AddAppearanceToDataTable("BROWN 1", 238, 59, 59)
        AddAppearanceToDataTable("BROWN 2", 205, 51, 51)
        AddAppearanceToDataTable("BROWN 3", 139, 35, 35)
        AddAppearanceToDataTable("BURLY WOOD", 222, 184, 135)
        AddAppearanceToDataTable("BURLY WOOD 1", 255, 211, 155)
        AddAppearanceToDataTable("BURLY WOOD 2", 238, 197, 145)
        AddAppearanceToDataTable("BURLY WOOD 3", 205, 170, 125)
        AddAppearanceToDataTable("BURLY WOOD 4", 139, 115, 85)
        AddAppearanceToDataTable("BURNT SIENNA", 138, 54, 15)
        AddAppearanceToDataTable("BURNT UMBER", 138, 51, 36)
        AddAppearanceToDataTable("CADET BLUE", 95, 158, 160)
        AddAppearanceToDataTable("CADET BLUE 1", 152, 245, 255)
        AddAppearanceToDataTable("CADET BLUE 2", 142, 229, 238)
        AddAppearanceToDataTable("CADET BLUE 3", 122, 197, 205)
        AddAppearanceToDataTable("CADET BLUE 4", 83, 134, 139)
        AddAppearanceToDataTable("CADMIUM ORANGE", 255, 97, 3)
        AddAppearanceToDataTable("CADMIUM YELLOW", 255, 153, 18)
        AddAppearanceToDataTable("CARROT", 237, 145, 33)
        AddAppearanceToDataTable("CHARTREUSE", 127, 255, 0)
        AddAppearanceToDataTable("CHARTREUSE 1", 118, 238, 0)
        AddAppearanceToDataTable("CHARTREUSE 2", 102, 205, 0)
        AddAppearanceToDataTable("CHARTREUSE 3", 69, 139, 0)
        AddAppearanceToDataTable("CHOCOLATE", 210, 105, 30)
        AddAppearanceToDataTable("CHOCOLATE 1", 255, 127, 36)
        AddAppearanceToDataTable("CHOCOLATE 2", 238, 118, 33)
        AddAppearanceToDataTable("CHOCOLATE 3", 205, 102, 29)
        AddAppearanceToDataTable("CHOCOLATE 4", 139, 69, 19)
        AddAppearanceToDataTable("COBALT", 61, 89, 171)
        AddAppearanceToDataTable("COBALT GREEN", 61, 145, 64)
        AddAppearanceToDataTable("COLD GREY", 128, 138, 135)
        AddAppearanceToDataTable("CORAL", 255, 127, 80)
        AddAppearanceToDataTable("CORAL 1", 255, 114, 86)
        AddAppearanceToDataTable("CORAL 2", 238, 106, 80)
        AddAppearanceToDataTable("CORAL 3", 205, 91, 69)
        AddAppearanceToDataTable("CORAL 4", 139, 62, 47)
        AddAppearanceToDataTable("CORNFLOWER BLUE", 100, 149, 237)
        AddAppearanceToDataTable("CORNSILK", 255, 248, 220)
        AddAppearanceToDataTable("CORNSILK 1", 238, 232, 205)
        AddAppearanceToDataTable("CORNSILK 2", 205, 200, 177)
        AddAppearanceToDataTable("CORNSILK 3", 139, 136, 120)
        AddAppearanceToDataTable("CRIMSON", 220, 20, 60)
        AddAppearanceToDataTable("CYAN", 0, 255, 255)
        AddAppearanceToDataTable("CYAN 2", 0, 238, 238)
        AddAppearanceToDataTable("CYAN 3", 0, 205, 205)
        AddAppearanceToDataTable("CYAN 4", 0, 139, 139)
        AddAppearanceToDataTable("DARK GOLDENROD", 184, 134, 11)
        AddAppearanceToDataTable("DARK GOLDENROD 1", 255, 185, 15)
        AddAppearanceToDataTable("DARK GOLDENROD 2", 238, 173, 14)
        AddAppearanceToDataTable("DARK GOLDENROD 3", 205, 149, 12)
        AddAppearanceToDataTable("DARK GOLDENROD 4", 139, 101, 8)
        AddAppearanceToDataTable("DARK GRAY", 169, 169, 169)
        AddAppearanceToDataTable("DARK GREEN", 0, 100, 0)
        AddAppearanceToDataTable("DARK KHAKI", 189, 183, 107)
        AddAppearanceToDataTable("DARK OLIVE GREEN", 85, 107, 47)
        AddAppearanceToDataTable("DARK OLIVE GREEN 1", 202, 255, 112)
        AddAppearanceToDataTable("DARK OLIVE GREEN 2", 188, 238, 104)
        AddAppearanceToDataTable("DARK OLIVE GREEN 3", 162, 205, 90)
        AddAppearanceToDataTable("DARK OLIVE GREEN 4", 110, 139, 61)
        AddAppearanceToDataTable("DARK ORANGE", 255, 140, 0)
        AddAppearanceToDataTable("DARK ORANGE 1", 255, 127, 0)
        AddAppearanceToDataTable("DARK ORANGE 2", 238, 118, 0)
        AddAppearanceToDataTable("DARK ORANGE 3", 205, 102, 0)
        AddAppearanceToDataTable("DARK ORANGE 4", 139, 69, 0)
        AddAppearanceToDataTable("DARK ORCHID", 153, 50, 204)
        AddAppearanceToDataTable("DARK ORCHID 1", 191, 62, 255)
        AddAppearanceToDataTable("DARK ORCHID 2", 178, 58, 238)
        AddAppearanceToDataTable("DARK ORCHID 3", 154, 50, 205)
        AddAppearanceToDataTable("DARK ORCHID 4", 104, 34, 139)
        AddAppearanceToDataTable("DARK SALMON", 233, 150, 122)
        AddAppearanceToDataTable("DARK SEA GREEN", 143, 188, 143)
        AddAppearanceToDataTable("DARK SEA GREEN 1", 193, 255, 193)
        AddAppearanceToDataTable("DARK SEA GREEN 2", 180, 238, 180)
        AddAppearanceToDataTable("DARK SEA GREEN 3", 155, 205, 155)
        AddAppearanceToDataTable("DARK SEA GREEN 4", 105, 139, 105)
        AddAppearanceToDataTable("DARK SLATE BLUE", 72, 61, 139)
        AddAppearanceToDataTable("DARK SLATE GRAY", 47, 79, 79)
        AddAppearanceToDataTable("DARK SLATE GRAY 1", 151, 255, 255)
        AddAppearanceToDataTable("DARK SLATE GRAY 2", 141, 238, 238)
        AddAppearanceToDataTable("DARK SLATE GRAY 3", 121, 205, 205)
        AddAppearanceToDataTable("DARK SLATE GRAY 4", 82, 139, 139)
        AddAppearanceToDataTable("DARK TURQUOISE", 0, 206, 209)
        AddAppearanceToDataTable("DARK VIOLET", 148, 0, 211)
        AddAppearanceToDataTable("DEEP PINK", 255, 20, 147)
        AddAppearanceToDataTable("DEEP PINK 1", 238, 18, 137)
        AddAppearanceToDataTable("DEEP PINK 2", 205, 16, 118)
        AddAppearanceToDataTable("DEEP PINK 3", 139, 10, 80)
        AddAppearanceToDataTable("DEEP SKYBLUE", 0, 191, 255)
        AddAppearanceToDataTable("DEEP SKYBLUE 1", 0, 178, 238)
        AddAppearanceToDataTable("DEEP SKYBLUE 2", 0, 154, 205)
        AddAppearanceToDataTable("DEEP SKYBLUE 3", 0, 104, 139)
        AddAppearanceToDataTable("DIM GRAY", 105, 105, 105)
        AddAppearanceToDataTable("DODGERBLUE", 30, 144, 255)
        AddAppearanceToDataTable("DODGERBLUE 1", 28, 134, 238)
        AddAppearanceToDataTable("DODGERBLUE 2", 24, 116, 205)
        AddAppearanceToDataTable("DODGERBLUE 3", 16, 78, 139)
        AddAppearanceToDataTable("EGGSHELL", 252, 230, 201)
        AddAppearanceToDataTable("EMERALD GREEN", 0, 201, 87)
        AddAppearanceToDataTable("FIREBRICK", 178, 34, 34)
        AddAppearanceToDataTable("FIREBRICK 1", 255, 48, 48)
        AddAppearanceToDataTable("FIREBRICK 2", 238, 44, 44)
        AddAppearanceToDataTable("FIREBRICK 3", 205, 38, 38)
        AddAppearanceToDataTable("FIREBRICK 4", 139, 26, 26)
        AddAppearanceToDataTable("FLESH", 255, 125, 64)
        AddAppearanceToDataTable("FLORAL WHITE", 255, 250, 240)
        AddAppearanceToDataTable("FOREST GREEN", 34, 139, 34)
        AddAppearanceToDataTable("GAINSBORO", 220, 220, 220)
        AddAppearanceToDataTable("GHOST WHITE", 248, 248, 255)
        AddAppearanceToDataTable("GOLD", 255, 215, 0)
        AddAppearanceToDataTable("GOLD 1", 238, 201, 0)
        AddAppearanceToDataTable("GOLD 2", 205, 173, 0)
        AddAppearanceToDataTable("GOLD 3", 139, 117, 0)
        AddAppearanceToDataTable("GOLDENROD", 218, 165, 32)
        AddAppearanceToDataTable("GOLDENROD 1", 255, 193, 37)
        AddAppearanceToDataTable("GOLDENROD 2", 238, 180, 34)
        AddAppearanceToDataTable("GOLDENROD 3", 205, 155, 29)
        AddAppearanceToDataTable("GOLDENROD 4", 139, 105, 20)
        AddAppearanceToDataTable("GRAY", 128, 128, 128)
        AddAppearanceToDataTable("GRAY 1", 3, 3, 3)
        AddAppearanceToDataTable("GRAY 2", 5, 5, 5)
        AddAppearanceToDataTable("GRAY 3", 8, 8, 8)
        AddAppearanceToDataTable("GRAY 4", 10, 10, 10)
        AddAppearanceToDataTable("GRAY 5", 13, 13, 13)
        AddAppearanceToDataTable("GRAY 6", 15, 15, 15)
        AddAppearanceToDataTable("GRAY 7", 18, 18, 18)
        AddAppearanceToDataTable("GRAY 8", 20, 20, 20)
        AddAppearanceToDataTable("GRAY 9", 23, 23, 23)
        AddAppearanceToDataTable("GRAY 10", 26, 26, 26)
        AddAppearanceToDataTable("GRAY 11", 28, 28, 28)
        AddAppearanceToDataTable("GRAY 12", 31, 31, 31)
        AddAppearanceToDataTable("GRAY 13", 33, 33, 33)
        AddAppearanceToDataTable("GRAY 14", 36, 36, 36)
        AddAppearanceToDataTable("GRAY 15", 38, 38, 38)
        AddAppearanceToDataTable("GRAY 16", 41, 41, 41)
        AddAppearanceToDataTable("GRAY 17", 43, 43, 43)
        AddAppearanceToDataTable("GRAY 18", 46, 46, 46)
        AddAppearanceToDataTable("GRAY 19", 48, 48, 48)
        AddAppearanceToDataTable("GRAY 20", 51, 51, 51)
        AddAppearanceToDataTable("GRAY 21", 54, 54, 54)
        AddAppearanceToDataTable("GRAY 22", 56, 56, 56)
        AddAppearanceToDataTable("GRAY 23", 59, 59, 59)
        AddAppearanceToDataTable("GRAY 24", 61, 61, 61)
        AddAppearanceToDataTable("GRAY 25", 64, 64, 64)
        AddAppearanceToDataTable("GRAY 26", 66, 66, 66)
        AddAppearanceToDataTable("GRAY 27", 69, 69, 69)
        AddAppearanceToDataTable("GRAY 28", 71, 71, 71)
        AddAppearanceToDataTable("GRAY 29", 74, 74, 74)
        AddAppearanceToDataTable("GRAY 30", 77, 77, 77)
        AddAppearanceToDataTable("GRAY 31", 79, 79, 79)
        AddAppearanceToDataTable("GRAY 32", 82, 82, 82)
        AddAppearanceToDataTable("GRAY 33", 84, 84, 84)
        AddAppearanceToDataTable("GRAY 34", 87, 87, 87)
        AddAppearanceToDataTable("GRAY 35", 89, 89, 89)
        AddAppearanceToDataTable("GRAY 36", 92, 92, 92)
        AddAppearanceToDataTable("GRAY 37", 94, 94, 94)
        AddAppearanceToDataTable("GRAY 38", 97, 97, 97)
        AddAppearanceToDataTable("GRAY 39", 99, 99, 99)
        AddAppearanceToDataTable("GRAY 40", 102, 102, 102)
        AddAppearanceToDataTable("GRAY 42", 107, 107, 107)
        AddAppearanceToDataTable("GRAY 43", 110, 110, 110)
        AddAppearanceToDataTable("GRAY 44", 112, 112, 112)
        AddAppearanceToDataTable("GRAY 45", 115, 115, 115)
        AddAppearanceToDataTable("GRAY 46", 117, 117, 117)
        AddAppearanceToDataTable("GRAY 47", 120, 120, 120)
        AddAppearanceToDataTable("GRAY 48", 122, 122, 122)
        AddAppearanceToDataTable("GRAY 49", 125, 125, 125)
        AddAppearanceToDataTable("GRAY 50", 127, 127, 127)
        AddAppearanceToDataTable("GRAY 51", 130, 130, 130)
        AddAppearanceToDataTable("GRAY 52", 133, 133, 133)
        AddAppearanceToDataTable("GRAY 53", 135, 135, 135)
        AddAppearanceToDataTable("GRAY 54", 138, 138, 138)
        AddAppearanceToDataTable("GRAY 55", 140, 140, 140)
        AddAppearanceToDataTable("GRAY 56", 143, 143, 143)
        AddAppearanceToDataTable("GRAY 57", 145, 145, 145)
        AddAppearanceToDataTable("GRAY 58", 148, 148, 148)
        AddAppearanceToDataTable("GRAY 59", 150, 150, 150)
        AddAppearanceToDataTable("GRAY 60", 153, 153, 153)
        AddAppearanceToDataTable("GRAY 61", 156, 156, 156)
        AddAppearanceToDataTable("GRAY 62", 158, 158, 158)
        AddAppearanceToDataTable("GRAY 63", 161, 161, 161)
        AddAppearanceToDataTable("GRAY 64", 163, 163, 163)
        AddAppearanceToDataTable("GRAY 65", 166, 166, 166)
        AddAppearanceToDataTable("GRAY 66", 168, 168, 168)
        AddAppearanceToDataTable("GRAY 67", 171, 171, 171)
        AddAppearanceToDataTable("GRAY 68", 173, 173, 173)
        AddAppearanceToDataTable("GRAY 69", 176, 176, 176)
        AddAppearanceToDataTable("GRAY 70", 179, 179, 179)
        AddAppearanceToDataTable("GRAY 71", 181, 181, 181)
        AddAppearanceToDataTable("GRAY 72", 184, 184, 184)
        AddAppearanceToDataTable("GRAY 73", 186, 186, 186)
        AddAppearanceToDataTable("GRAY 74", 189, 189, 189)
        AddAppearanceToDataTable("GRAY 75", 191, 191, 191)
        AddAppearanceToDataTable("GRAY 76", 194, 194, 194)
        AddAppearanceToDataTable("GRAY 77", 196, 196, 196)
        AddAppearanceToDataTable("GRAY 78", 199, 199, 199)
        AddAppearanceToDataTable("GRAY 79", 201, 201, 201)
        AddAppearanceToDataTable("GRAY 80", 204, 204, 204)
        AddAppearanceToDataTable("GRAY 81", 207, 207, 207)
        AddAppearanceToDataTable("GRAY 82", 209, 209, 209)
        AddAppearanceToDataTable("GRAY 83", 212, 212, 212)
        AddAppearanceToDataTable("GRAY 84", 214, 214, 214)
        AddAppearanceToDataTable("GRAY 85", 217, 217, 217)
        AddAppearanceToDataTable("GRAY 86", 219, 219, 219)
        AddAppearanceToDataTable("GRAY 87", 222, 222, 222)
        AddAppearanceToDataTable("GRAY 88", 224, 224, 224)
        AddAppearanceToDataTable("GRAY 89", 227, 227, 227)
        AddAppearanceToDataTable("GRAY 90", 229, 229, 229)
        AddAppearanceToDataTable("GRAY 91", 232, 232, 232)
        AddAppearanceToDataTable("GRAY 92", 235, 235, 235)
        AddAppearanceToDataTable("GRAY 93", 237, 237, 237)
        AddAppearanceToDataTable("GRAY 94", 240, 240, 240)
        AddAppearanceToDataTable("GRAY 95", 242, 242, 242)
        AddAppearanceToDataTable("GRAY 97", 247, 247, 247)
        AddAppearanceToDataTable("GRAY 98", 250, 250, 250)
        AddAppearanceToDataTable("GRAY 99", 252, 252, 252)
        AddAppearanceToDataTable("GREEN", 0, 255, 0)
        AddAppearanceToDataTable("GREEN 2", 0, 238, 0)
        AddAppearanceToDataTable("GREEN 3", 0, 205, 0)
        AddAppearanceToDataTable("GREEN 4", 0, 139, 0)
        AddAppearanceToDataTable("GREEN YELLOW", 173, 255, 47)
        AddAppearanceToDataTable("HONEYDEW", 240, 255, 240)
        AddAppearanceToDataTable("HONEYDEW 1", 224, 238, 224)
        AddAppearanceToDataTable("HONEYDEW 2", 193, 205, 193)
        AddAppearanceToDataTable("HONEYDEW 3", 131, 139, 131)
        AddAppearanceToDataTable("HOT PINK", 255, 105, 180)
        AddAppearanceToDataTable("HOT PINK 1", 255, 110, 180)
        AddAppearanceToDataTable("HOT PINK 2", 238, 106, 167)
        AddAppearanceToDataTable("HOT PINK 3", 205, 96, 144)
        AddAppearanceToDataTable("HOT PINK 4", 139, 58, 98)
        AddAppearanceToDataTable("INDIAN RED", 205, 92, 92)
        AddAppearanceToDataTable("INDIAN RED 1", 255, 106, 106)
        AddAppearanceToDataTable("INDIAN RED 2", 238, 99, 99)
        AddAppearanceToDataTable("INDIAN RED 3", 205, 85, 85)
        AddAppearanceToDataTable("INDIAN RED 4", 139, 58, 58)
        AddAppearanceToDataTable("INDIGO", 75, 0, 130)
        AddAppearanceToDataTable("IVORY", 255, 255, 240)
        AddAppearanceToDataTable("IVORY 1", 238, 238, 224)
        AddAppearanceToDataTable("IVORY 2", 205, 205, 193)
        AddAppearanceToDataTable("IVORY 3", 139, 139, 131)
        AddAppearanceToDataTable("IVORY BLACK", 41, 36, 33)
        AddAppearanceToDataTable("KELLY GREEN", 0, 128, 0)
        AddAppearanceToDataTable("KHAKI", 240, 230, 140)
        AddAppearanceToDataTable("KHAKI 1", 255, 246, 143)
        AddAppearanceToDataTable("KHAKI 2", 238, 230, 133)
        AddAppearanceToDataTable("KHAKI 3", 205, 198, 115)
        AddAppearanceToDataTable("KHAKI 4", 139, 134, 78)
        AddAppearanceToDataTable("LAVENDER", 230, 230, 250)
        AddAppearanceToDataTable("LAVENDER BLUSH", 255, 240, 245)
        AddAppearanceToDataTable("LAVENDER BLUSH 1", 238, 224, 229)
        AddAppearanceToDataTable("LAVENDER BLUSH 2", 205, 193, 197)
        AddAppearanceToDataTable("LAVENDER BLUSH 3", 139, 131, 134)
        AddAppearanceToDataTable("LAWN GREEN", 124, 252, 0)
        AddAppearanceToDataTable("LEMON CHIFFON", 255, 250, 205)
        AddAppearanceToDataTable("LEMON CHIFFON 1", 238, 233, 191)
        AddAppearanceToDataTable("LEMON CHIFFON 2", 205, 201, 165)
        AddAppearanceToDataTable("LEMON CHIFFON 3", 139, 137, 112)
        AddAppearanceToDataTable("LIGHT BLUE", 173, 216, 230)
        AddAppearanceToDataTable("LIGHT BLUE 1", 191, 239, 255)
        AddAppearanceToDataTable("LIGHT BLUE 2", 178, 223, 238)
        AddAppearanceToDataTable("LIGHT BLUE 3", 154, 192, 205)
        AddAppearanceToDataTable("LIGHT BLUE 4", 104, 131, 139)
        AddAppearanceToDataTable("LIGHT CORAL", 240, 128, 128)
        AddAppearanceToDataTable("LIGHT CYAN", 224, 255, 255)
        AddAppearanceToDataTable("LIGHT CYAN 1", 209, 238, 238)
        AddAppearanceToDataTable("LIGHT CYAN 2", 180, 205, 205)
        AddAppearanceToDataTable("LIGHT CYAN 3", 122, 139, 139)
        AddAppearanceToDataTable("LIGHT GOLDENROD", 255, 236, 139)
        AddAppearanceToDataTable("LIGHT GOLDENROD 1", 238, 220, 130)
        AddAppearanceToDataTable("LIGHT GOLDENROD 2", 205, 190, 112)
        AddAppearanceToDataTable("LIGHT GOLDENROD 3", 139, 129, 76)
        AddAppearanceToDataTable("LIGHT GOLDENROD YELLOW", 250, 250, 210)
        AddAppearanceToDataTable("LIGHT GREY", 211, 211, 211)
        AddAppearanceToDataTable("LIGHT PINK", 255, 182, 193)
        AddAppearanceToDataTable("LIGHT PINK 1", 255, 174, 185)
        AddAppearanceToDataTable("LIGHT PINK 2", 238, 162, 173)
        AddAppearanceToDataTable("LIGHT PINK 3", 205, 140, 149)
        AddAppearanceToDataTable("LIGHT PINK 4", 139, 95, 101)
        AddAppearanceToDataTable("LIGHT SALMON", 255, 160, 122)
        AddAppearanceToDataTable("LIGHT SALMON 1", 238, 149, 114)
        AddAppearanceToDataTable("LIGHT SALMON 2", 205, 129, 98)
        AddAppearanceToDataTable("LIGHT SALMON 3", 139, 87, 66)
        AddAppearanceToDataTable("LIGHT SEA GREEN", 32, 178, 170)
        AddAppearanceToDataTable("LIGHT SKY BLUE", 135, 206, 250)
        AddAppearanceToDataTable("LIGHT SKY BLUE 1", 176, 226, 255)
        AddAppearanceToDataTable("LIGHT SKY BLUE 2", 164, 211, 238)
        AddAppearanceToDataTable("LIGHT SKY BLUE 3", 141, 182, 205)
        AddAppearanceToDataTable("LIGHT SKY BLUE 4", 96, 123, 139)
        AddAppearanceToDataTable("LIGHT SLATE BLUE", 132, 112, 255)
        AddAppearanceToDataTable("LIGHT SLATE GRAY", 119, 136, 153)
        AddAppearanceToDataTable("LIGHT STEEL BLUE", 176, 196, 222)
        AddAppearanceToDataTable("LIGHT STEEL BLUE 1", 202, 225, 255)
        AddAppearanceToDataTable("LIGHT STEEL BLUE 2", 188, 210, 238)
        AddAppearanceToDataTable("LIGHT STEEL BLUE 3", 162, 181, 205)
        AddAppearanceToDataTable("LIGHT STEEL BLUE 4", 110, 123, 139)
        AddAppearanceToDataTable("LIGHT YELLOW 1", 255, 255, 224)
        AddAppearanceToDataTable("LIGHT YELLOW 2", 238, 238, 209)
        AddAppearanceToDataTable("LIGHT YELLOW 3", 205, 205, 180)
        AddAppearanceToDataTable("LIGHT YELLOW 4", 139, 139, 122)
        AddAppearanceToDataTable("LIME GREEN", 50, 205, 50)
        AddAppearanceToDataTable("LINEN", 250, 240, 230)
        AddAppearanceToDataTable("MAGENTA", 255, 0, 255)
        AddAppearanceToDataTable("MAGENTA 2", 238, 0, 238)
        AddAppearanceToDataTable("MAGENTA 3", 205, 0, 205)
        AddAppearanceToDataTable("MAGENTA 4", 139, 0, 139)
        AddAppearanceToDataTable("MANGANESE BLUE", 3, 168, 158)
        AddAppearanceToDataTable("MAROON", 128, 0, 0)
        AddAppearanceToDataTable("MAROON 1", 255, 52, 179)
        AddAppearanceToDataTable("MAROON 2", 238, 48, 167)
        AddAppearanceToDataTable("MAROON 3", 205, 41, 144)
        AddAppearanceToDataTable("MAROON 4", 139, 28, 98)
        AddAppearanceToDataTable("MEDIUM ORCHID", 186, 85, 211)
        AddAppearanceToDataTable("MEDIUM ORCHID 1", 224, 102, 255)
        AddAppearanceToDataTable("MEDIUM ORCHID 2", 209, 95, 238)
        AddAppearanceToDataTable("MEDIUM ORCHID 3", 180, 82, 205)
        AddAppearanceToDataTable("MEDIUM ORCHID 4", 122, 55, 139)
        AddAppearanceToDataTable("MEDIUM PURPLE", 147, 112, 219)
        AddAppearanceToDataTable("MEDIUM PURPLE 1", 171, 130, 255)
        AddAppearanceToDataTable("MEDIUM PURPLE 2", 159, 121, 238)
        AddAppearanceToDataTable("MEDIUM PURPLE 3", 137, 104, 205)
        AddAppearanceToDataTable("MEDIUM PURPLE 4", 93, 71, 139)
        AddAppearanceToDataTable("MEDIUM SEA GREEN", 60, 179, 113)
        AddAppearanceToDataTable("MEDIUM SLATE BLUE", 123, 104, 238)
        AddAppearanceToDataTable("MEDIUM SPRING GREEN", 0, 250, 154)
        AddAppearanceToDataTable("MEDIUM TURQUOISE", 72, 209, 204)
        AddAppearanceToDataTable("MEDIUM VIOLET RED", 199, 21, 133)
        AddAppearanceToDataTable("MELON", 227, 168, 105)
        AddAppearanceToDataTable("MIDNIGHT BLUE", 25, 25, 112)
        AddAppearanceToDataTable("MINT", 189, 252, 201)
        AddAppearanceToDataTable("MINT CREAM", 245, 255, 250)
        AddAppearanceToDataTable("MISTY ROSE", 255, 228, 225)
        AddAppearanceToDataTable("MISTY ROSE 1", 238, 213, 210)
        AddAppearanceToDataTable("MISTY ROSE 2", 205, 183, 181)
        AddAppearanceToDataTable("MISTY ROSE 3", 139, 125, 123)
        AddAppearanceToDataTable("MOCCASIN", 255, 228, 181)
        AddAppearanceToDataTable("NAVAJO WHITE", 255, 222, 173)
        AddAppearanceToDataTable("NAVAJO WHITE 1", 238, 207, 161)
        AddAppearanceToDataTable("NAVAJO WHITE 2", 205, 179, 139)
        AddAppearanceToDataTable("NAVAJO WHITE 3", 139, 121, 94)
        AddAppearanceToDataTable("NAVY", 0, 0, 128)
        AddAppearanceToDataTable("OLD LACE", 253, 245, 230)
        AddAppearanceToDataTable("OLIVE", 128, 128, 0)
        AddAppearanceToDataTable("OLIVE DRAB", 192, 255, 62)
        AddAppearanceToDataTable("OLIVE DRAB 1", 179, 238, 58)
        AddAppearanceToDataTable("OLIVE DRAB 2", 154, 205, 50)
        AddAppearanceToDataTable("OLIVE DRAB 3", 105, 139, 34)
        AddAppearanceToDataTable("ORANGE", 255, 128, 0)
        AddAppearanceToDataTable("ORANGE 1", 255, 165, 0)
        AddAppearanceToDataTable("ORANGE 2", 238, 154, 0)
        AddAppearanceToDataTable("ORANGE 3", 205, 133, 0)
        AddAppearanceToDataTable("ORANGE 4", 139, 90, 0)
        AddAppearanceToDataTable("ORANGE RED", 255, 69, 0)
        AddAppearanceToDataTable("ORANGE RED 1", 238, 64, 0)
        AddAppearanceToDataTable("ORANGE RED 2", 205, 55, 0)
        AddAppearanceToDataTable("ORANGE RED 3", 139, 37, 0)
        AddAppearanceToDataTable("ORCHID", 218, 112, 214)
        AddAppearanceToDataTable("ORCHID 1", 255, 131, 250)
        AddAppearanceToDataTable("ORCHID 2", 238, 122, 233)
        AddAppearanceToDataTable("ORCHID 3", 205, 105, 201)
        AddAppearanceToDataTable("ORCHID 4", 139, 71, 137)
        AddAppearanceToDataTable("PALE GOLDENROD", 238, 232, 170)
        AddAppearanceToDataTable("PALE GREEN", 152, 251, 152)
        AddAppearanceToDataTable("PALE GREEN 1", 154, 255, 154)
        AddAppearanceToDataTable("PALE GREEN 2", 144, 238, 144)
        AddAppearanceToDataTable("PALE GREEN 3", 124, 205, 124)
        AddAppearanceToDataTable("PALE GREEN 4", 84, 139, 84)
        AddAppearanceToDataTable("PALE TURQUOISE", 187, 255, 255)
        AddAppearanceToDataTable("PALE TURQUOISE 1", 174, 238, 238)
        AddAppearanceToDataTable("PALE TURQUOISE 2", 150, 205, 205)
        AddAppearanceToDataTable("PALE TURQUOISE 3", 102, 139, 139)
        AddAppearanceToDataTable("PALE VIOLET RED", 219, 112, 147)
        AddAppearanceToDataTable("PALE VIOLET RED 1", 255, 130, 171)
        AddAppearanceToDataTable("PALE VIOLET RED 2", 238, 121, 159)
        AddAppearanceToDataTable("PALE VIOLET RED 3", 205, 104, 137)
        AddAppearanceToDataTable("PALE VIOLET RED 4", 139, 71, 93)
        AddAppearanceToDataTable("PAPAYA WHIP", 255, 239, 213)
        AddAppearanceToDataTable("PEACH PUFF", 255, 218, 185)
        AddAppearanceToDataTable("PEACH PUFF 1", 238, 203, 173)
        AddAppearanceToDataTable("PEACH PUFF 2", 205, 175, 149)
        AddAppearanceToDataTable("PEACH PUFF 3", 139, 119, 101)
        AddAppearanceToDataTable("PEACOCK", 51, 161, 201)
        AddAppearanceToDataTable("PINK", 255, 192, 203)
        AddAppearanceToDataTable("PINK 1", 255, 181, 197)
        AddAppearanceToDataTable("PINK 2", 238, 169, 184)
        AddAppearanceToDataTable("PINK 3", 205, 145, 158)
        AddAppearanceToDataTable("PINK 4", 139, 99, 108)
        AddAppearanceToDataTable("PLUM", 221, 160, 221)
        AddAppearanceToDataTable("PLUM 1", 255, 187, 255)
        AddAppearanceToDataTable("PLUM 2", 238, 174, 238)
        AddAppearanceToDataTable("PLUM 3", 205, 150, 205)
        AddAppearanceToDataTable("PLUM 4", 139, 102, 139)
        AddAppearanceToDataTable("POWDER BLUE", 176, 224, 230)
        AddAppearanceToDataTable("PURPLE", 128, 0, 128)
        AddAppearanceToDataTable("PURPLE 1", 155, 48, 255)
        AddAppearanceToDataTable("PURPLE 2", 145, 44, 238)
        AddAppearanceToDataTable("PURPLE 3", 125, 38, 205)
        AddAppearanceToDataTable("PURPLE 4", 85, 26, 139)
        AddAppearanceToDataTable("RASPBERRY", 135, 38, 87)
        AddAppearanceToDataTable("RAW SIENNA", 199, 97, 20)
        AddAppearanceToDataTable("RED", 255, 0, 0)
        AddAppearanceToDataTable("RED 1", 238, 0, 0)
        AddAppearanceToDataTable("RED 2", 205, 0, 0)
        AddAppearanceToDataTable("RED 3", 139, 0, 0)
        AddAppearanceToDataTable("ROSY BROWN", 188, 143, 143)
        AddAppearanceToDataTable("ROSY BROWN 1", 255, 193, 193)
        AddAppearanceToDataTable("ROSY BROWN 2", 238, 180, 180)
        AddAppearanceToDataTable("ROSY BROWN 3", 205, 155, 155)
        AddAppearanceToDataTable("ROSY BROWN 4", 139, 105, 105)
        AddAppearanceToDataTable("ROYAL BLUE", 65, 105, 225)
        AddAppearanceToDataTable("ROYAL BLUE 1", 72, 118, 255)
        AddAppearanceToDataTable("ROYAL BLUE 2", 67, 110, 238)
        AddAppearanceToDataTable("ROYAL BLUE 3", 58, 95, 205)
        AddAppearanceToDataTable("ROYAL BLUE 4", 39, 64, 139)
        AddAppearanceToDataTable("SALMON", 250, 128, 114)
        AddAppearanceToDataTable("SALMON 1", 255, 140, 105)
        AddAppearanceToDataTable("SALMON 2", 238, 130, 98)
        AddAppearanceToDataTable("SALMON 3", 205, 112, 84)
        AddAppearanceToDataTable("SALMON 4", 139, 76, 57)
        AddAppearanceToDataTable("SANDY BROWN", 244, 164, 96)
        AddAppearanceToDataTable("SAP GREEN", 48, 128, 20)
        AddAppearanceToDataTable("SEA GREEN", 84, 255, 159)
        AddAppearanceToDataTable("SEA GREEN 1", 78, 238, 148)
        AddAppearanceToDataTable("SEA GREEN 2", 67, 205, 128)
        AddAppearanceToDataTable("SEA GREEN 3", 46, 139, 87)
        AddAppearanceToDataTable("SEASHELL", 255, 245, 238)
        AddAppearanceToDataTable("SEASHELL 1", 238, 229, 222)
        AddAppearanceToDataTable("SEASHELL 2", 205, 197, 191)
        AddAppearanceToDataTable("SEASHELL 3", 139, 134, 130)
        AddAppearanceToDataTable("SEPIA", 94, 38, 18)
        AddAppearanceToDataTable("SIENNA", 160, 82, 45)
        AddAppearanceToDataTable("SIENNA 1", 255, 130, 71)
        AddAppearanceToDataTable("SIENNA 2", 238, 121, 66)
        AddAppearanceToDataTable("SIENNA 3", 205, 104, 57)
        AddAppearanceToDataTable("SIENNA 4", 139, 71, 38)
        AddAppearanceToDataTable("SILVER", 192, 192, 192)
        AddAppearanceToDataTable("SKY BLUE", 135, 206, 235)
        AddAppearanceToDataTable("SKY BLUE 1", 135, 206, 255)
        AddAppearanceToDataTable("SKY BLUE 2", 126, 192, 238)
        AddAppearanceToDataTable("SKY BLUE 3", 108, 166, 205)
        AddAppearanceToDataTable("SKY BLUE 4", 74, 112, 139)
        AddAppearanceToDataTable("SLATE BLUE", 106, 90, 205)
        AddAppearanceToDataTable("SLATE BLUE 1", 131, 111, 255)
        AddAppearanceToDataTable("SLATE BLUE 2", 122, 103, 238)
        AddAppearanceToDataTable("SLATE BLUE 3", 105, 89, 205)
        AddAppearanceToDataTable("SLATE BLUE 4", 71, 60, 139)
        AddAppearanceToDataTable("SLATE GRAY", 112, 128, 144)
        AddAppearanceToDataTable("SLATE GRAY 1", 198, 226, 255)
        AddAppearanceToDataTable("SLATE GRAY 2", 185, 211, 238)
        AddAppearanceToDataTable("SLATE GRAY 3", 159, 182, 205)
        AddAppearanceToDataTable("SLATE GRAY 4", 108, 123, 139)
        AddAppearanceToDataTable("SNOW", 255, 250, 250)
        AddAppearanceToDataTable("SNOW 1", 238, 233, 233)
        AddAppearanceToDataTable("SNOW 2", 205, 201, 201)
        AddAppearanceToDataTable("SNOW 3", 139, 137, 137)
        AddAppearanceToDataTable("SPRING GREEN", 0, 255, 127)
        AddAppearanceToDataTable("SPRING GREEN 1", 0, 238, 118)
        AddAppearanceToDataTable("SPRING GREEN 2", 0, 205, 102)
        AddAppearanceToDataTable("SPRING GREEN 3", 0, 139, 69)
        AddAppearanceToDataTable("STEEL BLUE", 70, 130, 180)
        AddAppearanceToDataTable("STEEL BLUE 1", 99, 184, 255)
        AddAppearanceToDataTable("STEEL BLUE 2", 92, 172, 238)
        AddAppearanceToDataTable("STEEL BLUE 3", 79, 148, 205)
        AddAppearanceToDataTable("STEEL BLUE 4", 54, 100, 139)
        AddAppearanceToDataTable("TAN", 210, 180, 140)
        AddAppearanceToDataTable("TAN 1", 255, 165, 79)
        AddAppearanceToDataTable("TAN 2", 238, 154, 73)
        AddAppearanceToDataTable("TAN 3", 205, 133, 63)
        AddAppearanceToDataTable("TAN 4", 139, 90, 43)
        AddAppearanceToDataTable("TEAL", 0, 128, 128)
        AddAppearanceToDataTable("THISTLE", 216, 191, 216)
        AddAppearanceToDataTable("THISTLE 1", 255, 225, 255)
        AddAppearanceToDataTable("THISTLE 2", 238, 210, 238)
        AddAppearanceToDataTable("THISTLE 3", 205, 181, 205)
        AddAppearanceToDataTable("THISTLE 4", 139, 123, 139)
        AddAppearanceToDataTable("TOMATO", 255, 99, 71)
        AddAppearanceToDataTable("TOMATO 1", 238, 92, 66)
        AddAppearanceToDataTable("TOMATO 2", 205, 79, 57)
        AddAppearanceToDataTable("TOMATO 3", 139, 54, 38)
        AddAppearanceToDataTable("TURQUOISE", 64, 224, 208)
        AddAppearanceToDataTable("TURQUOISE 1", 0, 245, 255)
        AddAppearanceToDataTable("TURQUOISE 2", 0, 229, 238)
        AddAppearanceToDataTable("TURQUOISE 3", 0, 197, 205)
        AddAppearanceToDataTable("TURQUOISE 4", 0, 134, 139)
        AddAppearanceToDataTable("TURQUOISE BLUE", 0, 199, 140)
        AddAppearanceToDataTable("VIOLET", 238, 130, 238)
        AddAppearanceToDataTable("VIOLET RED", 208, 32, 144)
        AddAppearanceToDataTable("VIOLET RED 1", 255, 62, 150)
        AddAppearanceToDataTable("VIOLET RED 2", 238, 58, 140)
        AddAppearanceToDataTable("VIOLET RED 3", 205, 50, 120)
        AddAppearanceToDataTable("VIOLET RED 4", 139, 34, 82)
        AddAppearanceToDataTable("WARM GREY", 128, 128, 105)
        AddAppearanceToDataTable("WHEAT", 245, 222, 179)
        AddAppearanceToDataTable("WHEAT 1", 255, 231, 186)
        AddAppearanceToDataTable("WHEAT 2", 238, 216, 174)
        AddAppearanceToDataTable("WHEAT 3", 205, 186, 150)
        AddAppearanceToDataTable("WHEAT 4", 139, 126, 102)
        AddAppearanceToDataTable("WHITE", 255, 255, 255)
        AddAppearanceToDataTable("WHITE SMOKE", 245, 245, 245)
        AddAppearanceToDataTable("YELLOW", 255, 255, 0)
        AddAppearanceToDataTable("YELLOW 1", 238, 238, 0)
        AddAppearanceToDataTable("YELLOW 2", 205, 205, 0)
        AddAppearanceToDataTable("YELLOW 3", 139, 139, 0)
    End Sub


    Sub AddCADGEOMToFDSFile(ByVal FDSFileName As String, ByVal CADFileName As String)
        Dim FileNum1 As Integer = FreeFile()
        Dim a As String
        Dim i As Integer
        Dim CADFileRoot As String
        Dim LineCount As Integer
        Dim StatusRenderFile As String

        i = CADFileName.LastIndexOf("\")
        If i < 0 Then
            CADFileRoot = CADFileName
        Else
            CADFileRoot = CADFileName.Substring(i + 1)
        End If

        FileOpen(FileNum1, FDSFileName, OpenMode.Input, OpenAccess.Default, OpenShare.Default)

        Dim FileNum2 As Integer = FreeFile()
        FileOpen(FileNum2, "temp.fds", OpenMode.Output, OpenAccess.Default, OpenShare.Default)

        StatusRenderFile = False
        dlgStatus.ProgressBar1.Maximum = FDSLineCOunt
        LineCount = 0
        Do Until EOF(FileNum1)
            LineCount += 1
            If LineCount < dlgStatus.ProgressBar1.Maximum Then dlgStatus.ProgressBar1.Value = LineCount

            'Read every line of the FDS File
            a = LineInput(FileNum1)
            'IF it is a &DUMP Namelist
            If a.StartsWith("&DUMP") Then
                StatusRenderFile = True
                'If Render File variable does not exist
                If a.ToUpper.IndexOf("RENDER_FILE") < 0 Then
                    i = a.IndexOf("/")
                    If i < 0 Then
                        'IF / is not on the &DUMP line then add render file to end of line
                        a &= " RENDER_FILE='" & CADFileRoot & "'"
                    Else
                        'If / is on &DUMP line then put render file before /
                        a = a.Substring(0, i) & " RENDER_FILE='" & CADFileRoot & "'" & a.Substring(i)
                    End If
                End If
            End If
            If a.StartsWith("&TAIL") And StatusRenderFile = False Then
                'If &tail is found before the &Dump namelist then add the &DUMP Namelist with the RenderFile Variable
                StatusRenderFile = True
                PrintLine(FileNum2, "&DUMP  RENDER_FILE='" & CADFileRoot & "' /")
            End If
            PrintLine(FileNum2, a)
        Loop
        If StatusRenderFile = False Then
            'If EOF before the &Dump namelist then add the &DUMP Namelist with the RenderFile Variable
            PrintLine(FileNum2, "&DUMP  RENDER_FILE='" & CADFileRoot & "' /")
            PrintLine(FileNum2, "")
        End If

        FileClose(FileNum1)
        FileClose(FileNum2)
        FileCopy("temp.fds", FDSFileName)
        Kill("temp.fds")




    End Sub

    Sub GetFaceAppearanceIndexFromSURF_IDVariables(ByRef VariableNames() As String, ByRef VariableValues() As String, ByRef MaxAppearanceIndex As Integer, ByRef dv As DataView, ByRef FrontAppearance As Integer, Optional ByRef BackAppearance As Integer = 0, Optional ByRef LeftAppearance As Integer = 0, Optional ByRef RightAppearance As Integer = 0, Optional ByRef BottomAppearance As Integer = 0, Optional ByRef TopAppearance As Integer = 0)
        FrontAppearance = 0
        BackAppearance = 0
        LeftAppearance = 0
        RightAppearance = 0
        BottomAppearance = 0
        TopAppearance = 0

        Dim SURFID, SurfIDs() As String
        Dim AppearanceIndex As Integer
        Dim j As Integer
        For j = 0 To VariableNames.GetUpperBound(0)
            If VariableNames(j).StartsWith("SURF_ID") Then
                SURFID = VariableValues(j)
                SURFID = SURFID.Replace("'", "")
                SurfIDs = SURFID.Split(",")
                Select Case SurfIDs.GetUpperBound(0)
                    Case 0 'Only one surf
                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(0), dv, MaxAppearanceIndex)
                        FrontAppearance = AppearanceIndex
                        BackAppearance = AppearanceIndex
                        LeftAppearance = AppearanceIndex
                        RightAppearance = AppearanceIndex
                        BottomAppearance = AppearanceIndex
                        TopAppearance = AppearanceIndex

                    Case 2 ' surf ids Top,Sides,Bottom
                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(0), dv, MaxAppearanceIndex)
                        TopAppearance = AppearanceIndex

                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(1), dv, MaxAppearanceIndex)
                        FrontAppearance = AppearanceIndex
                        BackAppearance = AppearanceIndex
                        LeftAppearance = AppearanceIndex
                        RightAppearance = AppearanceIndex

                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(2), dv, MaxAppearanceIndex)
                        BottomAppearance = AppearanceIndex


                    Case 5
                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(0), dv, MaxAppearanceIndex)
                        LeftAppearance = AppearanceIndex

                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(1), dv, MaxAppearanceIndex)
                        RightAppearance = AppearanceIndex

                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(2), dv, MaxAppearanceIndex)
                        FrontAppearance = AppearanceIndex

                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(3), dv, MaxAppearanceIndex)
                        BackAppearance = AppearanceIndex

                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(4), dv, MaxAppearanceIndex)
                        BottomAppearance = AppearanceIndex

                        AppearanceIndex = GetAppearanceIndexFromSURFID(SurfIDs(5), dv, MaxAppearanceIndex)
                        TopAppearance = AppearanceIndex
                End Select

            End If
        Next


    End Sub

    Function GetAppearanceIndexFromSURFID(ByVal SurfID As String, ByRef DVAppearance As DataView, ByRef MaxAppearanceIndex As Integer, Optional ByVal DefaultAppearanceIndex As Integer = 0) As Integer
        Dim AppearanceIndex As Integer
        AppearanceIndex = DefaultAppearanceIndex
        DVAppearance.RowFilter = "Description='" & SurfID & "'"
        If DVAppearance.Count > 0 Then
            If DVAppearance(0).Item("AppearanceIndex") Is DBNull.Value Then
                MaxAppearanceIndex += 1
                DVAppearance(0).Item("AppearanceIndex") = MaxAppearanceIndex
            End If
            AppearanceIndex = DVAppearance(0).Item("AppearanceIndex")
        End If
        Return AppearanceIndex
    End Function
End Module
