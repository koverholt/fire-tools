Module modFortranNameList
    Public Surfaces() As String
    Public DatabaseAppearances() As String
    Public SurfaceProperties() As String

    Public Obstructions() As String
    Public ObstructionProperties() As String
    Public Vents() As String
    Public VentProperties() As String

    Public Appearances() As String
    Public AppearanceIDs() As String
    Sub ReadNameListFileIntoArray(ByVal Filename As String, ByRef b() As String)
        Dim a, Delimitor As String
        Dim i, j As Integer
        Dim x As System.IO.FileInfo = New System.IO.FileInfo(Filename)
        If Not x.Exists Then
            MsgBox("can not find file " & Chr(13) & Filename)
            Exit Sub
        End If
        FileOpen(1, Filename, OpenMode.Binary)
        If Err.Number <> 0 Then
            Exit Sub
        End If

        On Error GoTo 0
        a = Space(LOF(1))
        FileGet(1, a, 1)
        FileClose(1)

        Delimitor = "&"
        a = a.Replace(Chr(10), " ")
        a = a.Replace(Chr(13), " ")
        Do While a.IndexOf("  ") > 0
            a = a.Replace("  ", " ")
        Loop
        Do While a.IndexOf(" =") > 0
            a = a.Replace(" =", "=")
        Loop
        Do While a.IndexOf("= ") > 0
            a = a.Replace("= ", "=")
        Loop

        ParseDelimitedString(a, Delimitor, b)

    End Sub


    Sub ReadNameListFile(ByVal Filename As String)
        Dim b() As String = Nothing
        Dim i As Integer

        Dim Namelisttype As String = ""
        Dim ID As String = ""
        Dim Variablenames() As String = Nothing
        Dim VariableValues() As String = Nothing

        ReadNameListFileIntoArray(Filename, b)
        ReDim SurfaceProperties(0)
        SurfaceProperties(0) = ""
        FDSLineCOunt = b.GetUpperBound(0)
        COuntVentsWithXB = 0
        dlgStatus.ProgressBar1.Maximum = FDSLineCOunt
        For i = 1 To b.GetUpperBound(0) - 1
            dlgStatus.ProgressBar1.Value = i
            If b(i).StartsWith("SURF") Then
                ParseNameList(b(i), Surfaces, SurfaceProperties)
            ElseIf b(i).StartsWith("OBST") Then
                ParseNameList(b(i), Obstructions, ObstructionProperties)
            ElseIf b(i).StartsWith("VENT") Then
                ParseNameList(b(i), Vents, VentProperties)
                If CStr(VentProperties(VentProperties.GetUpperBound(0))).ToUpper.Replace(" ", "").IndexOf("XB=") >= 0 Then
                    COuntVentsWithXB += 1
                End If

            End If

        Next

    End Sub
    Public Sub ParseDelimitedString(ByVal a As String, ByVal Delimitor As String, ByRef b() As String)
        ' This routine separates a comma delimitted string into the array b$().
        ' The number of separated values is placed in position b$(0)
        Dim Index As Integer
        Dim i As Integer
        Dim j As Integer
        Dim k As Integer
        Dim CountDelimitor As Integer
        j = 1
        Index = 0
        i = InStr(a, Delimitor)

        If i = 0 Then
            ReDim b(2)
            b(0) = CStr(1)
            b(1) = a
        Else
            'Count number of delimeters
            For k = 1 To Len(a)
                If Mid(a, k, 1) = Delimitor Then
                    CountDelimitor = CountDelimitor + 1
                    If (CountDelimitor Mod 20000) = 0 Then
                        'Me.lblStatus.Text = "Counting Line " & (CountDelimitor) : System.Windows.Forms.Application.DoEvents()
                    End If

                End If
            Next
            ReDim b(CountDelimitor + 1)
            Do While i >= j
                If i - j > 1 Then
                    Index = Index + 1
                    If Mid(a, i - 1, 1) <> Chr(13) Then

                        b(Index) = Mid(a, j, i - j)
                    Else
                        b(Index) = Mid(a, j, (i - j) - 1)
                    End If
                    'A$ = Right$(A$, Len(A$) - j)
                    If (Index Mod 20000) = 0 Then
                        'Me.lblStatus.Text = "Reading Line " & (Index) : System.Windows.Forms.Application.DoEvents()
                    End If
                End If
                If Not (b(Index) Is Nothing) Then
                    If Asc((b(Index).Substring(0, 1))) = 9 Then
                        '    If Asc(VB.Left(b(Index), 1)) = 9 Then
                        b(Index) = b(Index).Substring(1)
                    End If
                End If
                j = i + 1
                i = InStr(j, a, Delimitor)
            Loop
            Index = Index + 1
            b(Index) = Mid(a, j, Len(a) - j + 1)
            b(0) = Index.ToString 'VB6.Format(Index)
        End If

    End Sub
    Private Function CleanNameList(ByVal a As String) As String
        Dim b As String = ""
        Dim i As Integer
        a = a.Trim
        a = a.Replace(Chr(10), " ")
        a = a.Replace(Chr(13), " ")
        If a.Length > 0 Then
            b = a.Chars(0)
        End If
        For i = 1 To a.Length - 1
            If b.EndsWith(" ") Then
                If a.Chars(i) <> " " Then
                    b = b & a.Chars(i)
                End If
            Else
                b = b & a.Chars(i)
            End If

        Next
        Do While b.IndexOf("= ") > 0
            b = b.Replace("= ", "=")
        Loop
        Do While b.IndexOf(" =") > 0
            b = b.Replace(" =", "=")
        Loop

        CleanNameList = b
    End Function
    Private Sub ParseNameList(ByVal a As String, ByRef Surfaces() As String, ByRef DatabaseSurfaceProperties() As String)
        Dim VariableCount, i, J As Integer
        Dim ID As String = ""
        Dim NamelistParameters As String
        a = CleanNameList(a)
        VariableCount = 0
        'Count = to find number of variables
        For i = 0 To a.Length - 1
            If a.Chars(i) = "=" Then
                VariableCount += 1
            End If
        Next

        'Find ID
        i = a.IndexOf(" ID=")
        If i > 0 Then
            J = a.IndexOf("'", i + 5)
            ID = a.Substring(i + 5, J - (i + 5))
        End If
        a = a.Replace(" ID='" & ID & "'", "")
        NamelistParameters = a.Substring(5)
        If Surfaces Is Nothing Then
            ReDim Surfaces(0)
            ReDim DatabaseSurfaceProperties(0)
        Else
            ReDim Preserve Surfaces(Surfaces.GetUpperBound(0) + 1)
            ReDim Preserve DatabaseSurfaceProperties(DatabaseSurfaceProperties.GetUpperBound(0) + 1)
        End If
        Surfaces(Surfaces.GetUpperBound(0)) = ID
        DatabaseSurfaceProperties(DatabaseSurfaceProperties.GetUpperBound(0)) = NamelistParameters
    End Sub

    Public Sub ParseNameList(ByVal NameList As String, ByRef NameListType As String, ByRef ID As String, ByRef VariableNames() As String, ByRef VariableValues() As String)
        Dim VariableCount, i, j, k As Integer
        Dim VariableIndex As Integer

        'Reset variables
        NameListType = ""
        ID = ""


        NameList = CleanNameList(NameList)
        If NameList = "" Then Exit Sub
        If NameList.Length < 5 Then Exit Sub

        'Make everything after the '/' a comment variable
        NameList = NameList.Replace("/", " Comment=")


        'Count '=' to find number of variables
        VariableCount = 0
        For i = 0 To NameList.Length - 1
            If NameList.Chars(i) = "=" Then
                VariableCount += 1
            End If
        Next

        'Get Namelist type
        NameListType = NameList.Substring(0, 4).ToUpper

        'Find ID
        i = NameList.IndexOf(" ID=")
        If i > 0 Then
            J = NameList.IndexOf("'", i + 5)
            ID = NameList.Substring(i + 5, J - (i + 5))
        End If

        'Parse namelist variables into array
        If VariableCount > 0 Then
            '    If Not (VariableNames Is Nothing) And Not (VariableValues Is Nothing) Then
            ReDim VariableNames(VariableCount - 1)
            ReDim VariableValues(VariableCount - 1)
            'NameList = NameList.Substring(5)

            Dim b() As String
            b = NameList.Split("=")
            VariableNames(0) = b(0).Trim
            VariableIndex = 0
            For i = 1 To b.GetUpperBound(0)
                b(i) = b(i).Trim
                j = b(i).LastIndexOf(" ")
                K = b(i).LastIndexOf(",")
                If j > -1 Or k > -1 Then
                    If j > k Then
                        If i <= VariableNames.GetUpperBound(0) Then
                            VariableNames(i) = b(i).Substring(j).Trim

                        End If
                        VariableValues(i - 1) = b(i).Substring(0, j).Trim

                    Else
                        If i <= VariableNames.GetUpperBound(0) Then
                            VariableNames(i) = b(i).Substring(j).Trim

                        End If

                        VariableValues(i - 1) = b(i).Substring(0, k).Trim

                    End If
                    If VariableValues(i - 1).EndsWith(",") Then VariableValues(i - 1) = VariableValues(i - 1).Substring(0, VariableValues(i - 1).Length - 1)
                End If
            Next
            'End If
        End If
    End Sub

End Module
